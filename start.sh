
cd ./service
nohup python main.py --device 'cuda:0'
echo "Start service complete!"


cd ..
echo "" > front.log
nohup pnpm dev > front.log &
echo "Start front complete!"
tail -f front.log
