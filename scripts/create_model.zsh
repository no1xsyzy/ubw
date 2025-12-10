#!/bin/zsh

UPPER_SNAKE="$1"
LOWER_SNAKE="$(echo $1 | tr '[:upper:]' '[:lower:]')"
CAPITAL_CASE="$(echo $1 | awk -F_ '{for (i=1; i<=NF; i++) {printf "%s", toupper(substr($i, 1, 1)) tolower(substr($i, 2))}}')"

IN_FILE="output/unknown_cmd/${UPPER_SNAKE}.json"
OUT_FILE="src/ubw/models/blive/${LOWER_SNAKE}.py"
TMP_NAME="_tmp_create_model"

if [ ! -f "$IN_FILE" ]; then
  echo "$IN_FILE not exists"
  exit 2
fi

jq -s '.[0]' "$IN_FILE" >${TMP_NAME}.json

datamodel-codegen \
  --target-python-version "3.12" \
  --additional-imports "._base.*" \
  --class-name "${CAPITAL_CASE}CommandInfo" \
  --input-file-type "json" --input "${TMP_NAME}.json" \
  --output-model-type "pydantic_v2.BaseModel" --output "${TMP_NAME}.py"

cat >"$OUT_FILE" <<EOF
$(cat ${TMP_NAME}.py)


class ${CAPITAL_CASE}Command(${CAPITAL_CASE}CommandInfo, CommandModel):
    cmd: Literal['${UPPER_SNAKE}']
EOF

rm -f "${TMP_NAME}.json" "${TMP_NAME}.py"

echo "lines should be checked:"
grep -E "time|color|Any" "${OUT_FILE}"
