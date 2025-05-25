# Das Skript für die Challenge des Monats 2025-05.
#
# Die Challenge des Monats ist:
# Wer füllt am meisten !coffee nach?!

from db import query

res = query(
    "SELECT user, user_id, count(*) as total FROM executed_commands "
    "WHERE command == 'coffee' "
    "AND timestamp BETWEEN '2025-05-01' AND '2025-06-01'"
    "AND user <> 'thefayras'"
    "GROUP BY user ORDER BY total DESC",
    ()
)

viewers = res[0:3]
top_three = [f"{ind + 1}. {x[0]} ({x[2]})" for ind, x in enumerate(viewers)]
top_three_ids = [x[0] for x in viewers]
print(top_three_ids)
if len(top_three) == 0:
    return_value = ("Keiner auf dem Leaderboard. Sei der/die Erste!", [])
else:
    return_value = (", ".join(top_three), top_three_ids)
