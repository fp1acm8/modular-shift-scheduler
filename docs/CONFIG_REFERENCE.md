# Configuration Reference

The scheduler expects an Excel workbook with two sheets named **Employees** and **Shifts**. Column
names are case-insensitive; spaces are ignored.

## Employees sheet

| Column | Required | Description |
| ------ | -------- | ----------- |
| `id` | ✅ | Unique identifier for the employee (string). |
| `name` | ✅ | Friendly name. |
| `skills` | ✅ | Comma-separated list of skills. Stored in lowercase without whitespace. |
| `max_hours_per_week` | ✅ | Maximum number of hours the employee can work in the planning horizon. |
| `cost_per_hour` | ❌ | Hourly cost. Defaults to `0` if omitted. |

## Shifts sheet

| Column | Required | Description |
| ------ | -------- | ----------- |
| `id` | ✅ | Unique identifier for the shift. |
| `start` | ✅ | ISO-8601 datetime string or Excel datetime cell. Must align to slot boundaries. |
| `end` | ✅ | ISO-8601 datetime string or Excel datetime cell later than start. |
| `required_skill` | ✅ | Skill required for the shift. |
| `required_employees` | ✅ | Number of employees needed. |
| `weight` | ❌ | Multiplier applied to shortage penalties. Defaults to `1`. |

## Solver options

Optional solver tuning parameters are exposed in `SchedulingConfig`:

- `slot_minutes` (default `60`): length of a discrete time slot.
- `shortage_penalty_per_employee` (default `100`): penalty applied per unfilled employee per shift.

These can be modified programmatically after loading the configuration:

```python
config = load_config_from_excel("config.xlsx")
config.slot_minutes = 30
config.shortage_penalty_per_employee = 250
```
