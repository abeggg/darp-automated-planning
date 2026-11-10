#!/usr/bin/env bash
set -euo pipefail

FD="${FD:-./fast-downward.py}"
PYP="${PYP:-pyperplan}"
OPTIC="${OPTIC:-./optic-clp}"
VAL="${VAL:-Validate}"

mkdir -p external_results

# Pyperplan: valida a versao STRIPS. O comando oficial usa 'gbf'.
for p in easy medium hard very-hard; do
  "$PYP" -H hff -s gbf pddl/darp-strips.pddl "pddl/${p}-strips.pddl" \
    > "external_results/pyperplan-${p}.txt" 2>&1 || true
done

# Fast Downward: versao com custos. A* + LM-cut busca custo otimo.
for p in easy medium hard very-hard; do
  "$FD" pddl/darp-cost.pddl "pddl/${p}-cost.pddl" --search "astar(lmcut())" \
    > "external_results/fd-astar-${p}.txt" 2>&1 || true
  "$FD" --alias lama-first pddl/darp-cost.pddl "pddl/${p}-cost.pddl" \
    > "external_results/fd-lama-${p}.txt" 2>&1 || true
done

# OPTIC: extensao temporal.
"$OPTIC" pddl/darp-temporal.pddl pddl/temporal-example.pddl \
  > external_results/optic-temporal.txt 2>&1 || true

# VAL: se os planners produzirem planos em arquivo, valide-os com o formato abaixo.
# "$VAL" pddl/darp-cost.pddl pddl/medium-cost.pddl plano.plan

echo "Execucoes finalizadas. Veja external_results/."
