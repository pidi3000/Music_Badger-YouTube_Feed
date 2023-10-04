source .venv/bin/activate

echo ""
echo "##################################################"
echo "CELERY stop"
echo "##################################################"
./dev_support_scripts/celery_shutdown.sh

echo ""
echo "##################################################"
echo "REDIS stop"
echo "##################################################"
./dev_support_scripts/redis_stop.sh