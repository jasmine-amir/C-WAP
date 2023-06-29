#!/bin/bash -e

# Check if the conda directory exists. If not, make one.
if ! [[ -d ./conda ]]; then
    mkdir ./conda
fi

# List of env's to build:
# env_list[<env name>]="<env contents>"
declare -A env_list
env_list[env-bowtie2]="bowtie2=2.4.5"
env_list[env-minimap2]="minimap2=2.24"
env_list[env-ivar]="ivar=1.3.1"
env_list[env-samtools]="samtools=1.15"
env_list[env-kraken2]="kraken2=2.1.2 bracken=2.7"
env_list[env-python]="python=3.8.1 matplotlib scikit-learn=1.1.1 pandas"
env_list[env-bcftools]="bcftools=1.15"
env_list[env-pangolin]="pangolin=4.1.2"
env_list[env-kallisto]="kallisto=0.48"
env_list[env-entrez-direct]="entrez-direct=16.2"
env_list[env-gs-wkhtmltopdf]="openssl=1.0 wkhtmltopdf=0.12.4 ghostscript=9.54"


# Loop through all env's one by one.
# If not already present, create the env and store under c-wap/conda subdirectory.
for env_name in ${!env_list[@]}; do
    if ! [[ -d conda/${env_name} ]]; then
        echo Creating ${env_name}...
        conda create -c bioconda -c conda-forge -c defaults --mkdir --yes --quiet --prefix conda/${env_name} ${env_list[${env_name}]}
        echo Created ${env_name}.
    else
        echo ${env_name} already exists, skipped.
    fi
done

# Micromamba v1.0.0 for Freyja v1.3.12+, JA 2023 03 16
if ! [[ -d conda/env-freyja ]]; then
    echo Creating env-freyja...
    mamba_flags="-c bioconda -c conda-forge -c defaults --yes --quiet"
    micromamba create ${mamba_flags} --prefix conda/env-freyja freyja=1.4.4 
    echo Created env-freyja
else
    echo env-freyja already exists, skipped.
fi


exit 0
