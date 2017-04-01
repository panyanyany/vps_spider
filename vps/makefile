clean:
	echo > logs/routines.log && echo > logs/output.log

t:
	echo > logs/routines.log && python tests/t.py 2>&1 | tee logs/output.log

crawl:
	echo > logs/routines.log 
	echo > logs/output.log 
	scrapy crawl plan 2>&1 | tee logs/output.log

.PHONY: t, clean
