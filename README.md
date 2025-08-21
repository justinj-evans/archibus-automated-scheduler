# Archibus-Automated-Scheduler
> [!CAUTION]
> As of July 2025, Archibus blocks IP requests from GitHub Runners.  
> Use this repository only for educational purposes.

![Latest Scheduled Run](https://github.com/justinj-evans/archibus-automated-scheduler/actions/workflows/workflow.yml/badge.svg)

We’ve all been there — it's Monday morning, and you suddenly remember you forgot to book your workstation. Now you're rushing through Archibus, hoping workstation 28 isn’t already taken by that one colleague who always beats you to it.

Enter the Archibus-Automated-Scheduler! This tool automatically books your in-office days, so you’ll never have to scramble again. No more stress — just smooth and effortless scheduling.

# Setup Instructions
Follow the steps below to configure and use the Archibus Automated Scheduler:
1. **Fork the Repository**  
Start by [forking](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#forking-a-repository) this repository to your GitHub account. 

2. **Assign Secret to the Repository**   
The assigned secret will contain the necessary login credentials and scheduling parameters (username, password, building, etc.).

3. **Schedule In-Office Days**  
Uncomment the repository's Github Action to start the scheduler. Following instruction below to modify the cron job to match your in-office days.

## Assign Secret to the Repository
> [!WARNING]   
GitHub secrets for username and password are encrypted and hidden, never appearing in logs or the repository. This keeps credentials secure during workflow execution. Users must follow departmental security guidelines.

To create secrets on Github see linked [instructions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository). In your repository, assign a GitHub secret with the name: ARCHIBUS_SCHEDULING_ARGS. The secret should be formatted as follows:

- username: Your Archibus username (case-insensitive).
- password: Your Archibus password (case-insensitive).
- building_name: The building name for booking. Use the first word (e.g., 'Jean') or hyphenate multi-word name (e.g., 'Jean-Talon').
- floor: The floor acronym and number, e.g., 'JT01'.
- workstation: The workstation number to reserve, e.g., '111'.

Example secret
```
--username=your_username --password=your_password --building_name=your-building --floor=XX01 --workstation=111
```

## Schedule In-Office Days
> [!WARNING] 
Users are responsible for ensuring their bookings are properly managed. Be sure to cancel any reservations directly through Archibus if they are no longer needed to avoid overbooking or unused reservations.

As days become available, one month in advance, the Archibus-Automated-Scheduler is set to search for and book your workstation. To start the scheduler uncomment the cron job in the repository Github Action:
*.github\workflows\action.yml* . 

### Syntax
A cron schedule consists of 5 fields, each representing a specific unit of time, followed by the days of the week. The format is:
```
* * * * *
| | | | |
| | | | └─ Day of the week (0 - 7) (Sunday = 0 or 7)
| | | └─── Month (1 - 12)
| | └───── Day of the month (1 - 31)
| └─────── Hour (0 - 23)
└───────── Minute (0 - 59)
```

### Customizing the Schedule

You can adjust the schedule to fit your preferred in-office days. For example, the schedule below is set to run at 9:00 AM UTC / 5:00 AM ETC on Monday, Wednesday, and Friday.

```
schedule:
  - cron: "0 9 * * 1,3,5"
```

## Contributors
Contributions of any kind welcome.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/justinj-evans/archibus-automated-scheduler/blob/main/LICENSE) file for details.
