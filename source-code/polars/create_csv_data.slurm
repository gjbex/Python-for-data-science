#!/usr/bin/env -S bash -l
#SBATCH --account=lpt2_sysadmin
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=01:00:00
#SBATCH --mail-user=geertjan.bex@uhasselt.be
#SBATCH --mail-type=FAIL,END

module purge
module load Python/3.11.3-GCCcore-12.3.0

# This should generate a file of approximately 6 GB
python ./create_csv_data.py \
    --files 1 \
    --cols 100 \
    --rows 2500000 \
    large_data
