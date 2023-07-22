#!/bin/zsh

UPPER_SNAKE="$1"
LOWER_SNAKE="$(echo $1 | tr '[:upper:]' '[:lower:]')"
CAPITAL_CASE="$(echo $1 | awk -F_ '{for (i=1; i<=NF; i++) {printf "%s", toupper(substr($i, 1, 1)) tolower(substr($i, 2))}}')"

IN_FILE="output/unknown_cmd/${UPPER_SNAKE}.json"
OUT_FILE="src/blivedm/models/${LOWER_SNAKE}.py"
TMP_NAME="_tmp_create_model"

jq -s '.[0]' "$IN_FILE" > ${TMP_NAME}.json

poetry run datamodel-codegen --input ${TMP_NAME}.json --output ${TMP_NAME}.py --input-file-type json

cat >"$OUT_FILE" << EOF
from ._base import *


$(cat ${TMP_NAME}.py | head -n-8 | tail -n+10)


class ${CAPITAL_CASE}Command(CommandModel):
    cmd: Literal['${UPPER_SNAKE}']
    data: Data

EOF

rm -f "${TMP_NAME}.json" "${TMP_NAME}.py"
