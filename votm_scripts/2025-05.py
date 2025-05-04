# Das Skript für die Challenge des Monats 2025-05.
#
# Die Challenge des Monats ist:
# Wer füllt am meisten !coffee nach?!

from db import query

res = query(
    "SELECT user, count(*) as total FROM executed_commands "
    "WHERE command == 'coffee' "
    "AND timestamp BETWEEN '2025-05-01' AND '2025-06-01'"
    "AND user <> 'thefayras'"
    "GROUP BY user ORDER BY total DESC",
    ()
)

top_three = [f"{ind + 1}. {x[0]} ({x[1]})" for ind, x in enumerate(res[0:3])]
if len(top_three) == 0:
    return_value = "Keiner auf dem Leaderboard. Sei der/die Erste!"
else:
    return_value = ", ".join(top_three)
