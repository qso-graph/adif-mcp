clear
echo "Developer Commands"
echo "--------------------------------------------------------------------------------------------------------"
grep -E '^[a-zA-Z0-9_.-]+:.*?##'  Makefile | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $1, $2}'
printf "\n"
