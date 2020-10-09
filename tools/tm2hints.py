"""
Converts transMap genePred entries into Augustus hints

TODO: This uses different logic from calculate_num_missing_introns in the classify module. This could be confusing.
The challenge here is that transMap PSL objects may be negative stranded, may have indels at gaps, and have a
chromosomal target.

This process also uses a larger fuzz distance under the idea that more wiggle room is allowed here before we provide
Augustus a chance at fixing the problem. We are more stringent when evaluating the results.
"""
from . import procOps

cmd = [
    "transMap2hints.pl",
    "--ep_cutoff=0",
    "--ep_margin=12",
    "--min_intron_len=50",
    "--start_stop_radius=5",
    "--tss_tts_radius=10",
    "--utrend_cutoff=10",
    "--in=/dev/stdin",
    "--out=/dev/stdout",
]


def tm_to_hints(tm_tx, tm_psl, ref_psl):
    """
    Converts a genePred transcript to hints parseable by Augustus.

    :param tm_tx: GenePredTranscript object for transMap transcript
    :param ref_psl: PslRow object for the relationship between the source transcript and genome as made by
    GenePredToFakePsl
    :param tm_psl: PslRow object for the relationship between tm_tx and ref_tx
    :return: GFF formatted string.
    """
    ref_starts = fix_ref_q_starts(ref_psl)
    intron_vector = ["1" if is_fuzzy_intron(i, tm_psl, ref_starts) else "0" for i in tm_tx.intron_intervals]
    tm_gp = "\t".join(tm_tx.get_gene_pred())
    tm_rec = "".join([tm_gp, "\t", ",".join(intron_vector), "\n"])
    return procOps.popen_catch(cmd, tm_rec)


def fix_ref_q_starts(ref_psl):
    """
    Inverts a negative strand reference psl. Needed for fuzzy intron determination.
    :param ref_psl: PslRow object generated by GenePredToFakePsl
    :return: list
    """
    if ref_psl.strand == "-":
        ref_starts = [
            ref_psl.q_size - (ref_psl.q_starts[i] + ref_psl.block_sizes[i]) for i in range(len(ref_psl.q_starts))
        ]
    else:
        ref_starts = ref_psl.q_starts
    return ref_starts


def is_fuzzy_intron(intron, tm_psl, ref_starts, fuzz_distance=12):
    """
    Determines if a intron is within fuzz distance of its aligned partner.
    :param intron: ChromosomeInterval for this intron
    :param tm_psl: PslRow object for the relationship between tm_tx and ref_tx
    :param ref_starts: list of transcript coordinates that are intron boundaries in the reference transcript
    :param fuzz_distance: max distance allowed to be moved in transcript coordinate space
    :return: boolean
    """
    q_gap_start = tm_psl.target_coordinate_to_query(intron.start - 1)
    q_gap_stop = tm_psl.target_coordinate_to_query(intron.stop)
    fuzzed_start = q_gap_start - fuzz_distance
    fuzzed_stop = q_gap_stop + fuzz_distance
    r = [fuzzed_start <= ref_gap <= fuzzed_stop for ref_gap in ref_starts]
    return any(r)
