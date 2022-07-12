"""
Find Motifs ...
"""

import subprocess
from pathlib import Path

from latch import small_task, large_task, workflow
from latch.types import LatchFile, LatchDir


@large_task
def find_motif_task(bam: LatchFile) -> LatchDir:
    # Step 1
    tag_directory = Path("peak_tag_dir").resolve()

    _HOMER_tag_dir_cmd = [
        "makeTagDirectory",
        str(tag_directory),
        bam.local_path
    ]

    subprocess.run(_HOMER_tag_dir_cmd)

    # Step 2
    peak_text_file = Path("peaks.txt").resolve()

    _HOMER_findPeaks_cmd = [
        "findPeaks",
        str(tag_directory),
        "-style",
        "histone",
        "-nfr",
        "-region",
        "-size",
        "1000",
        "-L",
        "2",
        "-o",
        str(peak_text_file)
    ]

    subprocess.run(_HOMER_findPeaks_cmd)

    # Task 3
    peaks_bed_file = Path("peaks.bed").resolve()

    _HOMER_make_bed_cmd = [
        "pos2bed.pl",
        str(peak_text_file),
        "-o",
        str(peaks_bed_file)
    ]

    subprocess.run(_HOMER_make_bed_cmd)

    # Task 4
    motifs_directory = Path("motif_output_directory").resolve()

    _HOMER_motifs_cmd = [
        "findMotifsGenome.pl",
        str(peaks_bed_file),
        "hg38",
        str(motifs_directory),
        "-size",
        "200"
    ]

    subprocess.run(_HOMER_motifs_cmd)

    return LatchDir(str(motifs_directory), "latch:///motif_output_directory")


@workflow
def call_motifs(bam: LatchFile) -> LatchDir:
    """Homer-Motif analyzes genomic positions for enriched motifs. 

    Homer-Motif
    ----

    Homer-Motif calls peaks using homer motif callers and analyzes the genomic positions for enriched motifs.

    __metadata__:
        display_name: HOMER motif caller
        author:
            name: annalijh
            email: anna.li3@mail.mcgill.ca
            github: https://github.com/TheMatrixMaster
        repository: https://github.com/TheMatrixMaster/homer-motif-latch-wf
        license:
            id: MIT

    Args:

        bam:
          Input bam file to find enriched motifs

          __metadata__:
            display_name: Input bam file


        
    """

    return find_motif_task(bam=bam)

