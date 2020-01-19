[cmdletbinding()]
Param(
    [string]$command = ""
)

switch ($command)
{
    "format" {
        Write-Host "python -m black --line-length 120 --target-version py38 ."
        python -m black --line-length 120 --target-version py38 .
        exit $LASTEXITCODE
    }
    "checkstyle" {
        Write-Host "python -m black --line-length 120 --target-version py38 --check ."
        python -m black --line-length 120 --target-version py38 --check .
        exit $LASTEXITCODE
    }
}

Write-Host `
"Usage:
  Make <command>

Commands:
  format                       Format all .py files in this directory.
  checkstyle                   Check which .py files in this directory need reformatting."
