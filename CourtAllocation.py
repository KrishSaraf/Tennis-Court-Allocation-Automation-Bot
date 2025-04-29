import pandas as pd
import os


def process_rally_data(file_path, priority_members):
    rallyData = pd.read_excel(file_path)
    rallyData['Tele Handle'] = rallyData['Tele Handle'].astype(str).apply(lambda x: '@' + x if not x.startswith('@') else x)
    
    # Record the original order of the DataFrame
    rallyData['original_order'] = rallyData.index
    # Set the smallest possible timestamp for priority members
    smallest_possible_timestamp = pd.Timestamp('1970-01-01 00:00:00')
    rallyData.loc[rallyData['Tele Handle'].isin(priority_members), 'Timestamp'] = smallest_possible_timestamp

    # Reorder the DataFrame based on the Timestamp column
    rallyData = rallyData.sort_values(by=['Timestamp', 'original_order'])
    rallyData.reset_index(drop=True, inplace=True)
    rallyData.drop(columns=['original_order'], inplace=True)
    
    # Reset the index after sorting
    rallyData.reset_index(drop=True, inplace=True)
    rallyData.loc[:, 'Skill'] = rallyData['Your Skill Level'].str.split().str[0]

    return rallyData

def sort_groups_by_timestamp_sum(groups):
    # Calculate cumulative sum of timestamps for each group and sort
    groups_sorted = sorted(groups, key=lambda group: group['Timestamp'].astype('int64').sum())
    return groups_sorted

def session_court_allocation(df, flag, grouped_names, max_coaching=9, court_capacity=4):
    groups = []

    if flag:
        # Allocate Coaching first for sessions with coaching
        coaching_needed = df[df['Your Skill Level'].str.contains('Coaching') & (~df['Name'].isin(grouped_names))].head(max_coaching)
        groups.append(coaching_needed)
        grouped_names.extend(coaching_needed['Name'].tolist())  # Mark coaching as grouped

    df = df[~df['Your Skill Level'].str.contains('Coaching')].reset_index(drop=True)

    # Function to add players to a group
    def add_players_to_group(current_group, group):
        for player in group.iterrows():
            if len(current_group) < court_capacity:
                if player[1]['Name'] not in grouped_names:
                    current_group.append(player[1])
                    grouped_names.append(player[1]['Name'])  # Mark as grouped
            else:
                break
        return current_group

    # Iterate through rows and group players
    for index, row in df.iterrows():
        if row['Name'] in grouped_names:
            continue  # Skip if already grouped

        current_group = [row]
        grouped_names.append(row['Name'])  # Mark as grouped

        if row['Skill'] == 'Advanced':
            eligible_players = df[(df['Skill'].isin(['Advanced', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
            current_group = add_players_to_group(current_group, eligible_players)

        elif row['Skill'] == 'Beginner':
            eligible_players = df[(df['Skill'].isin(['Beginner', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
            current_group = add_players_to_group(current_group, eligible_players)

        elif row['Skill'] == 'Intermediate':
            eligible_players = df[(df['Skill'].isin(['Advanced', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
            current_group = add_players_to_group(current_group, eligible_players)

            if len(current_group) < court_capacity:
                eligible_players = df[(df['Skill'].isin(['Beginner', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
                current_group = add_players_to_group(current_group, eligible_players)

        groups.append(pd.DataFrame(current_group))

    return groups, grouped_names

def save_court_allocation_to_file(session_name, court_allocation, court_count):
    file_name = f"Session_{session_name}_Court_Allocation.txt"
    
    with open(file_name, "w") as file:
        for i, group in enumerate(court_allocation[:court_count]):
            group_name = determine_group_name(group)
            file.write(f"Group {i+1} ({group_name}):\n")
            for name in group['Name']:
                file.write(f"{name:<30}\n")
            file.write("\n\n")
    
    print(f"Saved {court_count} groups to '{file_name}'")
    # for i, group in enumerate(court_allocation):
    #     print(f"Group {i + 1}:")
    #     print(group[['Name', 'Skill']])
    #     print()  # Add an empty line for better readability
    # print([name for group in court_allocation[:court_count] for name in group['Name'].tolist()])
    return [name for group in court_allocation[:court_count] for name in group['Name'].tolist()]

def determine_group_name(group):
    if all(group['Skill'] == 'New'):
        return 'Coaching'
    elif all(group['Skill'] == 'Advanced'):
        return 'Advanced'
    elif all(group['Skill'] == 'Beginner'):
        return 'Beginner'
    elif all(group['Skill'] == 'Intermediate'):
        return 'Intermediate'
    elif set(group['Skill']) == {'Beginner', 'Intermediate'}:
        return 'Beginner/Intermediate'
    else:
        return 'Advanced/Intermediate'

def save_ungrouped_players(ungrouped_players_df, session_column, marker="(Priority)"):
    with open("Ungrouped_Players.txt", "w") as file:
        file.write("Ungrouped Players:\n")
        for _, player in ungrouped_players_df.iterrows():
            name_with_marker = f"{player['Name']}"
            if player['Timestamp'] == pd.Timestamp('1970-01-01 00:00:00'):
                name_with_marker += f" {marker}"  # Append marker to the name

            file.write(f"Name: {name_with_marker}, Skill: {player['Skill']}, Session: {player[session_column]}\n")

    print(f"Saved ungrouped players to 'Ungrouped_Players.txt'")

def check_duplicates_in_file(file_name):
    if not os.path.exists(file_name):
        print(f"File {file_name} does not exist.")
        return
    
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    # Extract names from the file (assuming each name starts after the group label)
    names = []
    for line in lines:
        if line.strip() and not line.startswith("Group") and not line.startswith("Ungrouped Players"):
            names.append(line.strip())
    
    # Check for duplicates
    duplicates = [name for name in set(names) if names.count(name) > 1]
    if duplicates:
        print(f"Warning: Duplicate names found in {file_name}:")
        for duplicate in duplicates:
            print(f" - {duplicate}")
    else:
        print(f"No duplicate names found in {file_name}.")

def remove_duplicates_keep_newest(df):
    """
    This function removes older records based on the 'Name' and 'Tele Handle'.
    It keeps the newest record for each 'Name' and 'Tele Handle' combination
    based on the 'Timestamp' column.
    """
    # Convert the 'Timestamp' column to datetime if not already
    df_unique = df.sort_values(by='Timestamp', ascending=False).drop_duplicates(subset='Tele Handle', keep='first').reset_index(drop=True)
    df_unique = df_unique.sort_values(by='Timestamp', ascending=True).reset_index(drop=True)
    return df_unique

def run_allocation_process():
    priority_members=[] # Add all the telegram ids of the people given priority access
#     priority_members = [
#     '@Oomint', '@thiriiiiiii', '@garg0003', '@ujjwal24agarwal', '@ArttuHannila', '@aribruhhh', 
#     '@atsh1220', '@jingjonglingmong', '@SwatowAnthony', '@paella_ella', '@Ananya_Jayanty', 
#     '@aladynnn', '@vverawen', '@rohanR25', '@alexwpribadi', '@KrishSaraf', '@jonnyquek',
#     '@utkarsh24agarwal', '@arav_behl', '@MatteZech', '@Vthoon', '@me', '@hyobin78', 
#     '@annabelqi1028', '@boyabyy', '@pterra2004', '@ar_ya_xx', '@ashfuton', '@AbhirajGupta', 
#     '@Benjamintdk', '@kaikotaku', '@pinkfrosteddonut', '@anneliese31220', '@minhthepham', 
#     '@Jk_Brendan', '@christinafujiapple', '@Gushi_sienn', '@salz_bonnie','@PRASHANTAG017','@nardogg'
# ] 

    rallyData = process_rally_data('path to your excel', priority_members)
    rallyData=remove_duplicates_keep_newest(rallyData)

    session_column = 'Which session would you like to attend? (can select multiple, you\'ll be allocated ONE based on availability)'
    
    session_a_tuesday = rallyData[rallyData[session_column].str.contains('Session A', na=False)].reset_index()
    session_b_tuesday = rallyData[rallyData[session_column].str.contains('Session B', na=False)].reset_index()
    session_c_thursday = rallyData[rallyData[session_column].str.contains('Session C', na=False)].reset_index()
    
    # Gather user inputs
    flag_a = input("Will session A have coaching? (y/n): ").strip().lower() == "y"
    flag_b = input("Will session B have coaching? (y/n): ").strip().lower() == "y"
    flag_c = input("Will session C have coaching? (y/n): ").strip().lower() == "y"

    A_count = int(input("How many courts for session A? "))
    B_count = int(input("How many courts for session B? "))
    C_count = int(input("How many courts for session C? "))

    # Create session list
    sessions = [('A', session_a_tuesday, flag_a, A_count),
                ('B', session_b_tuesday, flag_b, B_count),
                ('C', session_c_thursday, flag_c, C_count)]

    # Sort sessions by the number of courts
    sessions.sort(key=lambda x: x[3], reverse=True)

    all_grouped_players = []
    Allocated_players=[]
    for session_name, session_df, flag, court_count in sessions:
        court_allocation, grouped_names = session_court_allocation(session_df, flag, all_grouped_players)
        grouped_players = save_court_allocation_to_file(session_name, court_allocation, court_count)
        Allocated_players.extend(grouped_players)
        all_grouped_players.extend(grouped_players)
    
    # print(all_grouped_players)
    ungrouped_players_df = rallyData[~rallyData['Name'].isin(Allocated_players)]
    save_ungrouped_players(ungrouped_players_df, session_column)

    check_duplicates_in_file("Session_A_Court_Allocation.txt")
    check_duplicates_in_file("Session_B_Court_Allocation.txt")
    check_duplicates_in_file("Session_C_Court_Allocation.txt")
    check_duplicates_in_file("Ungrouped_Players.txt")

def main():
    run_allocation_process()

if __name__ == "__main__":
    main()
