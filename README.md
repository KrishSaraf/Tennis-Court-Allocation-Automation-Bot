# 🎾 Tennis Code Allocation Automation Bot

An algorithm for automated tennis court allocation for members using a constraint satisfaction technique, reducing manual time by over 90% each week. This system processes member registration data, allocates courts based on skill levels and priorities, and outputs final groupings for each session automatically.

## How to Use

1. Download your week's registration file (e.g., `Week 13 Rally Registration Form (Responses).xlsx`).

2. Open the Python script(CourtAllocation.py) and update the file path inside the code:
   - Find this line: 
     ```python
     rallyData = process_rally_data('.xlsx path', priority_members)
     ```
   - Replace the path with your own week's Excel file location if different.

3. Run the script: CourtAllocation.py

4. Follow on-screen prompts:
   - Specify if any session has Coaching.
   - Enter the number of courts available for each session.

5. Outputs generated:
   - Court allocation text files for each session (e.g., `Session_A_Court_Allocation.txt`).
   - `Ungrouped_Players.txt` showing players who couldn't be allocated.

## Technology & Logic Used

### Language:
- Python 🐍

### Libraries:
- `pandas` for data processing
- `os` for file handling

### Algorithmic Approach:
- **Constraint Satisfaction**: Priority members are force-allocated early.
- **Skill-Based Grouping**: Players are matched by skill (Advanced, Intermediate, Beginner, Coaching).
- **Timestamp Prioritization**: Earlier registrants get higher preference.
- **Dynamic Court Filling**: Each court group is filled up to a maximum capacity intelligently.
- **Duplicate Handling**: Latest player registrations are kept; older ones are removed automatically.
- **Sentinel Flags**: Sessions with coaching are handled separately first.

### Optimization Focus:
- Removed manual checking
- Fast scalable allocation across sessions 🚀

## Result
✅ Saved over 90% manual time every week  
✅ Generated court allocations instantly  
✅ No human errors, no duplicate entries!
