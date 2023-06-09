from metaflow import FlowSpec, step
import subprocess

class LinearFlow(FlowSpec):

    @step
    def start(self):
        self.result = ""
        self.next(self.fastqc)

    @step
    def fastqc(self):
        subprocess.run("fastqc SRR24451057.fastq --outdir outputMetaflow", shell= True)
        subprocess.run("mv ./outputMetaflow/SRR24451057_fastqc.html ./outputMetaflow/qcreport.html", shell= True)
        self.next(self.minimap_instrument)
    @step
    def minimap_instrument(self):
        subprocess.run("./minimap2/minimap2 -d ./outputMetaflow/index.mmi ecoli.fna", shell = True)
        subprocess.run("./minimap2/minimap2 -a ./outputMetaflow/index.mmi SRR24451057.fastq > ./outputMetaflow/alignments.sam", shell = True)
        self.next(self.samtools_view)

    @step
    def samtools_view(self):
        subprocess.run("samtools view -b ./outputMetaflow/alignments.sam -o ./outputMetaflow/alignments.bam", shell = True)
        self.next(self.samtools_flagstat)

    @step
    def samtools_flagstat(self):
        subprocess.run("samtools flagstat ./outputMetaflow/alignments.bam > ./outputMetaflow/flagstat.txt", shell = True)
        self.next(self.check_quality)
    @step
    def check_quality(self):
        percent_str = ""
        percent_val = 0
        with open("./outputMetaflow/flagstat.txt") as f:
            for line in f:
                if "mapped" in line and not "primary" in line:
                    percent_str = line.split("(")[1].split("%")[0]
                    percent_val = float(percent_str)
                    break
        if percent_val > 90:
            print("OK")
            self.result = "OK"
        else:
            print("NOT OK")
            self.result = "NOT OK"
        self.next(self.samtools_sort)
    @step
    def samtools_sort(self):
        if (self.result != "NOT OK"):
            subprocess.run("samtools sort -o ./output/alignments.sorted.bam ./output/alignments.bam", shell = True)
        self.next(self.freebayes)
    @step
    def freebayes(self):
        if (self.result != "NOT OK"):
            subprocess.run("freebayes -f ecoli.fna ./output/alignments.sorted.bam > ./output/result.vcf", shell = True)
        self.next(self.end)
    @step
    def end(self):
        print("Done")
if __name__ == '__main__':
    flow = LinearFlow()
