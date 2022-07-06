"""
Find Motifs ...
"""

import subprocess
from pathlib import Path

from latch import small_task, workflow
from latch.types import LatchFile, LatchDir


# make the index file
@small_task
def index_task(bam: LatchFile) -> (LatchFile):
    # reference to the output
    bam_index_file = Path("index_of_bam.bam").resolve()

    _samtools_index_cmd = [
        "samtools",
        "index",
        bam.local_path,
    ]

    subprocess.run(_samtools_index_cmd)

    return LatchFile(str(bam_index_file), "latch:///index_of_bam.bam")


# makes tag directory
@small_task
def make_tagDirectory_task(bam: LatchFile) -> (LatchDir):
    # A reference to our output.
    tag_directory = Path("peak-tagdir").resolve()

    _HOMER_tagdir_cmd = [
        "makeTagDirectory",
        str(tag_directory),
        bam.local_path
    ]

    subprocess.run(_HOMER_tagdir_cmd)

    return LatchDir(str(tag_directory), "latch:///peak-tagdir")


# creates the text file for the peaks
@small_task
def peak_textfile_task(tagdir: LatchDir) -> LatchFile:
    peaktext_file = Path("peaks.txt").resolve()

    _HOMER_findPeaks_cmd = [
        "findPeaks",
        tagdir.local_path,
        "-style",
        "histone",
        "-nfr",
        "-region",
        "-size",
        "1000",
        "-L",
        "2",
        "-o",
        str(peaktext_file)
    ]

    subprocess.run(_HOMER_findPeaks_cmd)

    return LatchFile(str(peaktext_file), "latch:///peaks.txt")


# makes the homer bed file
@small_task
def peak_bedfile_task(peaktextfile: LatchFile) -> LatchFile:
    peak_bed_file = Path("peaks.bed").resolve()

    _HOMER_makebed_cmd = [
        "pos2bed.pl",
        peaktextfile.local_path,
        ">",
        str(peak_bed_file)
    ]

    subprocess.run(_HOMER_makebed_cmd)

    return LatchFile(str(peak_bed_file), "latch:///peaks.bed")


# finding motifs
@small_task
def find_motif_task(peaksbed: LatchFile) -> LatchDir:
    motifs_directory = Path("motif_output_directory").resolve()

    _HOMER_motifs_cmd = [
        "findMotifsGenome.pl",
        peaksbed.local_path,
        "hg38",
        str(motifs_directory),
        "-size",
        "200"
    ]

    subprocess.run(_HOMER_motifs_cmd)

    return LatchDir(str(motifs_directory), "latch:///motif_output_directory")


@small_task
def sort_bam_task(sam: LatchFile) -> LatchFile:
    bam_file = Path("covid_sorted.bam").resolve()

    _samtools_sort_cmd = [
        "samtools",
        "sort",
        "-o",
        str(bam_file),
        "-O",
        "bam",
        sam.local_path,
    ]

    subprocess.run(_samtools_sort_cmd)

    return LatchFile(str(bam_file), "latch:///covid_sorted.bam")


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
        license:
            id: MIT

    Args:

        bam:
          Input bam file to find enriched motifs

          __metadata__:
            display_name: Input bam file


        
    """
    index_file = index_task(bam=bam)
    tagdir = make_tagDirectory_task(bam=bam)
    peaktextfile = peak_textfile_task(tagdir=tagdir)
    peaksbed = peak_bedfile_task(peaktextfile=peaktextfile)
    return find_motif_task(peaksbed=peaksbed)


if __name__ == "__main__":
    call_motifs(bam=LatchFile("/Users/annali/Downloads/annaliworkflow/data/ENCFF835YDD.bam"))
