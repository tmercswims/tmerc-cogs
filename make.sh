case $1 in
    format)
        echo "python -m black --line-length 120 --target-version py38 ."
        python -m black --line-length 120 --target-version py38 .
        exit $?
        ;;
    checkstyle)
        echo "python -m black --line-length 120 --target-version py38 --check ."
        python -m black --line-length 120 --target-version py38 --check .
        exit $?
        ;;
esac

echo \
"Usage:
  make <command>

Commands:
  format                       Format all .py files in this directory.
  checkstyle                   Check which .py files in this directory need reformatting."
