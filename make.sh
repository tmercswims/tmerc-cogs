case $1 in
    format)
        echo "python -m black ."
        python -m black .
        exit $?
        ;;
    checkstyle)
        echo "python -m black--check ."
        python -m black --check .
        exit $?
        ;;
esac

echo \
"Usage:
  make <command>

Commands:
  format                       Format all .py files in this directory.
  checkstyle                   Check which .py files in this directory need reformatting."
