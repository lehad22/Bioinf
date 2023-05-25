#!/bin/bash

mkdir output
fastqc SRR24451057.fastq --outdir output
mv ./output/SRR24451057_fastqc.html ./output/qcreport.html

./minimap2/minimap2 -d ./output/index.mmi ecoli.fna

./minimap2/minimap2 -a ./output/index.mmi SRR24451057.fastq > ./output/alignments.sam

samtools view -b ./output/alignments.sam -o ./output/alignments.bam

samtools flagstat ./output/alignments.bam > ./output/flagstat.txt

result=$(python3 quality.py ./output/flagstat.txt)

echo "Сообщение: $result"

if [ "$result" == "OK" ]
then
  samtools sort -o ./output/alignments.sorted.bam ./output/alignments.bam
  freebayes -f ecoli.fna ./output/alignments.sorted.bam > ./output/result.vcf
  echo "Done"
fi
