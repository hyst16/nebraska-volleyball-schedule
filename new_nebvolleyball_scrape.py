import os
import requests
from bs4 import BeautifulSoup

# Directory where the logos are stored
logo_directory = 'Logos/'

# URL for the schedule page
url = "https://huskers.com/sports/volleyball/schedule"

# Send a GET request to the page to retrieve the HTML
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Scrape the overall and conference records
overall_record = ''
conference_record = ''
last_game_ranking = ''  # Store the most recent ranking

schedule_stats_section = soup.find('section', class_='schedule-stats')
if schedule_stats_section:
    # Find the overall record
    overall_record_item = schedule_stats_section.find('strong', string='Overall')
    if overall_record_item:
        overall_record = overall_record_item.find_next('strong', class_='schedule-stats-item__value').text

    # Find the conference record
    conf_record_item = schedule_stats_section.find('strong', string='Conf.')
    if conf_record_item:
        conference_record = conf_record_item.find_next('strong', class_='schedule-stats-item__value').text

# Function to get the logo filename
def get_logo_filename(team_name):
    # Create the filename based on the team name, replacing spaces with underscores
    logo_filename = f"{team_name.lower().replace(' ', '_')}.png"
    # Check if the logo file exists in the Logos directory
    if os.path.exists(os.path.join(logo_directory, logo_filename)):
        return logo_filename
    else:
        print(f"Logo for '{team_name}' not found.")
        return ''  # Return an empty string if the logo is not found

# Find all the schedule event items
schedule_items = soup.find_all('div', class_='schedule-event-item')

# Prepare to store the extracted data
schedule_data = []

for item in schedule_items:
    # Extract venue type (home, away, or neutral)
    venue_type = item.find('div', class_='schedule-event-venue__type')
    venue = venue_type.text.strip() if venue_type else 'Unknown'

    # Extract day and date
    date_div = item.find('div', class_='schedule-event-date__wrapper')
    day = date_div.find('time').text[:3] if date_div else 'N/A'  # Abbreviate day to 3 letters
    date = date_div.find('time', class_='schedule-event-date__label').text if date_div else 'N/A'

    # Extract result or time
    result = item.find('div', class_='schedule-event-item-result__label')
    if result:
        # If a result exists (game played), get the outcome (W or L) and score
        outcome = result.find('span').text.strip()  # Extract W or L
        score = result.text.replace(outcome, '').strip()  # Remove the outcome from the score
    else:
        # If game hasn't been played yet, extract time only
        result = item.find('div', class_='schedule-event-item-result')
        outcome = ''
        score = result.find('strong', class_='schedule-event-item-result__label').text if result else 'TBD'

    # Extract Nebraska's ranking and logo (assuming Nebraska logo is already saved manually)
    nebraska_rank = item.find('strong', class_='schedule-event-item-default__team-rank').text if item.find('strong', class_='schedule-event-item-default__team-rank') else ''
    
    # Capture the most recent ranking if available
    if nebraska_rank:
        last_game_ranking = nebraska_rank

    nebraska_logo_filename = get_logo_filename("Nebraska")  # Using manually saved "Nebraska.png"

    # Extract opponent's team name and ranking
    opponent_name = item.find('strong', class_='schedule-event-item-default__opponent-name').text if item.find('strong', class_='schedule-event-item-default__opponent-name') else ''
    opponent_rank = item.find_all('strong', class_='schedule-event-item-default__team-rank')[1].text.strip() if len(item.find_all('strong', class_='schedule-event-item-default__team-rank')) > 1 else ''
    
    # Remove any extra "#" in the opponent's rank
    if opponent_rank.startswith("##"):
        opponent_rank = opponent_rank.replace("##", "#")

    # Get the opponent's logo filename (manually saved in Logos folder)
    opponent_logo_filename = get_logo_filename(opponent_name)

    # Extract the game location
    location = item.find('div', class_='schedule-event-item-default__location').text if item.find('div', class_='schedule-event-item-default__location') else 'N/A'

    # Add extracted data to the schedule_data list
    schedule_data.append({
        'Venue': venue,
        'Day': day,
        'Date': date,
        'Result/Time': f"{score}",
        'Nebraska Rank': nebraska_rank,
        'Nebraska Logo': nebraska_logo_filename,
        'Opponent': opponent_name,
        'Opponent Rank': opponent_rank,
        'Opponent Logo': opponent_logo_filename,
        'Location': location,
        'Outcome': outcome
    })

# Generate HTML file with a compact table, floating logo, and overall/conference records
with open('nebraska_volleyball_schedule.html', 'w') as file:
    file.write(f'''<html>
<head>
    <title>Nebraska Volleyball Schedule</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: url('Arena.jpg') no-repeat center center fixed;
            background-size: cover;
            padding: 20px;
            color: white;
            font-size: 12px;
            display: flex;
            flex-direction: row;
        }}
        .left-section {{
            width: 40%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            position: relative;
        }}
        .left-section img {{
            width: 80%;
            margin-bottom: 5px;
            filter: drop-shadow(8px 8px 12px rgba(0, 0, 0, 0.9)); /* Heavier and darker drop shadow */
        }}
        .text-box {{
            background-color: rgba(0, 0, 0, 0.6); /* Semi-transparent black background */
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 10px;
        }}
        .ranking {{
            font-size: 36px;
            color: white;
            text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.9); /* Heavier and darker drop shadow for ranking */
            margin-bottom: 5px;
        }}
        .left-section h1 {{
            font-size: 42px;
            color: white;
            text-shadow: 6px 6px 10px rgba(0, 0, 0, 0.9); /* Heavier and darker drop shadow for VOLLEYBALL */
        }}
        .left-section h2, .left-section h3 {{
            font-size: 28px;
            text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.9); /* Heavier and darker drop shadow for overall and conf */
        }}
        table {{
            width: 60%;
            margin: auto;
            border-collapse: collapse;
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid #ddd;
            text-align: center;
            color: black;
        }}
        th, td {{
            padding: 2px;
            border: 1px solid #ddd;
            line-height: 1.0;
        }}
        th {{
            background-color: rgba(255, 255, 255, 0.7);
        }}
        td img {{
            vertical-align: middle;
            width: 40px;
            margin-right: 8px;
        }}
        td.left-align {{
            text-align: left;
        }}
        .outcome-w {{
            color: green;
        }}
        .outcome-l {{
            color: red;
        }}
        .date-info {{
            display: flex;
            justify-content: space-between;
        }}
    </style>
</head>
<body>
    <div class="left-section">
        <img src="Logos/nebraska.png" alt="Nebraska Logo">
        <div class="text-box">
            <h1>VOLLEYBALL</h1>''')

    # Display the ranking with "Current Ranking:" if available
    if last_game_ranking:
        file.write(f'<div class="ranking">Current Ranking: #{last_game_ranking.lstrip("#")}</div>')

    # Display Overall and Conf. records
    file.write(f'''
        <h2>Overall: {overall_record}</h2>
        <h3>Conf: {conference_record}</h3>
        </div>
    </div>
    <table>
        <tr>
            <th>Date</th>
            <th>Location</th>
            <th>Opponent</th>
            <th>W/L</th>
            <th>Score</th>
        </tr>''')

    for game in schedule_data:
        # Opponent logo, name, and ranking
        opponent_info = f"<img src='Logos/{game['Opponent Logo']}' alt='{game['Opponent']} Logo'> {game['Opponent']}" if not game['Opponent Rank'] else f"<img src='Logos/{game['Opponent Logo']}' alt='{game['Opponent']} Logo'> {game['Opponent Rank']} {game['Opponent']}"

        # Set color for W/L outcome
        outcome_class = "outcome-w" if game['Outcome'] == "W" else "outcome-l" if game['Outcome'] == "L" else ""

        # Write the table row for each game
        file.write(f'''
        <tr>
            <td><div class="date-info">{game['Date']}<span>{game['Day']}</span></div></td>
            <td>{game['Venue']}</td>
            <td class="left-align">{opponent_info}</td>
            <td class="{outcome_class}">{game['Outcome']}</td>
            <td>{game['Result/Time']}</td>
        </tr>''')

    file.write('''
    </table>
</body>
</html>''')

print("Schedule data has been scraped and saved to index.html.")
