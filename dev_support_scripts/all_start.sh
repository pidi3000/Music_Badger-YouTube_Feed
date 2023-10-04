source .venv/bin/activate

echo ""
echo "##################################################"
echo "REDIS start"
echo "##################################################"
./dev_support_scripts/redis_start.sh

echo ""
echo "##################################################"
echo "CELERY start"
echo "##################################################"
./dev_support_scripts/celery_start.sh


echo ""
echo "##################################################"
echo "CELERY DONE"
echo "##################################################"