to create a cronjob, run:
	crontab cronjob.txt
It will create a cron job with the specified time in that file, and will run the script.
Currently the cron job is set to run every two hours, and calls script.sh in the cron dir.

In order to set it up on your own machine, change the path in cronjob.txt and any additional changes needed for the script.sh itself.
