# Das Skript für die Challenge des Monats 2025-06.
#
# Die Challenge des Monats ist:
# Share some Love! Gib Kudos an andere. Wer am meisten Kudos bekommt, wird der VOTM!

from db import query

res = query(
    "SELECT user, json_extract (parameters, '$.recipient') as recipient, count(*) as total FROM executed_commands "
    "WHERE command == 'kudos' "
    "AND timestamp BETWEEN '2025-06-01' AND '2025-07-01'"
    "AND recipient <> 'thefayras'"
    "GROUP BY recipient ORDER BY total DESC",
    ()
)

viewers = res[0:3]
top_three = [f"{ind + 1}. ???" for ind, x in enumerate(viewers)]
top_three_ids = [x[0] for x in viewers]

if len(top_three) == 0:
    return_value = ("Noch niemand? Vergebe paar Kudos!", [])
else:
    return_value = (", ".join(top_three), top_three_ids)
