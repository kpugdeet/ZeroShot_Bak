for number in {0..4}
do
#    CUDA_VISIBLE_DEVICES=0 python3 main.py --KEY=APY --DIR=APY_Alexnet_Square_Original_$number --SELATT=1 --TA=1 --maxSteps=50 --OPT=2 --numClass=32 --numAtt=193
#    CUDA_VISIBLE_DEVICES=0 python3 main.py --KEY=APY --DIR=APY_Alexnet_Square_Original_$number --SELATT=1 --TC=1 --maxSteps=5000 --OPT=3 --numClass=32 --numAtt=193
    CUDA_VISIBLE_DEVICES=0 python3 main.py --KEY=APY --DIR=APY_Alexnet_Square_Original_$number --SELATT=1 --OPT=4 --numClass=32 --numAtt=193 > APY_Alexnet_Square_Original_$number.txt
done
