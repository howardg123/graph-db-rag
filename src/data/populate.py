import csv
import random
from faker import Faker

# Initialize the Faker generator
faker = Faker()

# Define departments and positions
departments = {
    "Engineering": {
        "employees": ["Developer", "Senior Developer"],
        "leads": ["Tech Lead"],
    },
    "Product": {
        "employees": ["Product Owner"],
        "leads": ["Project Manager"],
    },
    "Quality Assurance": {
        "employees": ["QA Developer", "Senior QA Developer"],
        "leads": ["QA Lead"],
    },
    "Finance": {
        "employees": ["Financial Analyst", "Accountant"],
        "leads": ["Finance Manager"],
        "projects": [None]  # No projects for finance
    },
    "Human Resources": {
        "employees": ["HR Specialist", "Recruiter"],
        "leads": ["HR Manager"],
        "projects": [None]  # No projects for HR
    }
}

# Define 30 cross-department projects with descriptive names
cross_department_projects = [
    "Customer Relationship Management System",
    "E-commerce Platform Revamp",
    "Mobile Application Development",
    "Data Analytics Dashboard",
    "Social Media Marketing Tool",
    "Inventory Management System",
    "Sales Performance Analysis",
    "Internal Communication Tool",
    "HR Management System",
    "User Experience Improvement Project",
    "Financial Reporting Automation",
    "Product Launch Campaign",
    "Web Application Security Enhancements",
    "Virtual Team Collaboration Platform",
    "Cloud Infrastructure Migration",
    "Artificial Intelligence Implementation",
    "Supply Chain Optimization",
    "Market Research Tool",
    "Online Learning Platform",
    "Feedback Collection System",
    "Task Management System",
    "Employee Engagement Initiative",
    "Performance Review Automation",
    "IT Asset Management System",
    "Customer Feedback Analysis",
    "Digital Payment Integration",
    "Compliance Management System",
    "Onboarding Process Improvement",
    "Data Privacy Compliance Project",
    "Product Quality Assurance Initiative"
]

# Parameters for balancing
EMPLOYEES_PER_LEAD = 6  # Each lead handles 6 employees
LEADS_PER_HEAD = 5      # Each department head handles 5 leads

# Create a CEO
CEO = {
    "id": 1,
    "full_name": faker.name(),
    "position": "CEO",
    "career_mentor": "",
    "tech_mentor": "",
    "project": None
}

# Generate 300 employees and distribute by department
total_employees = 300
employees = []
employee_id = 2

# Assign employees to departments
for department, roles in departments.items():
    # Skip HR and Finance for employee generation
    if department in ["Finance", "Human Resources"]:
        continue

    # Equal number of employees per relevant department
    dept_employee_count = total_employees // (len(departments) - 2)

    for _ in range(dept_employee_count):
        full_name = faker.name()
        position = random.choice(roles["employees"])
        employees.append({
            "id": employee_id,
            "full_name": full_name,
            "position": position,
            "department": department,
            "career_mentor": "",
            "tech_mentor": "",
            "project": []  # List for multiple project assignments
        })
        employee_id += 1

# Calculate number of leads needed per department based on EMPLOYEES_PER_LEAD
leads = []
lead_id = employee_id

for department, roles in departments.items():
    # Skip HR and Finance for lead generation
    if department in ["Finance", "Human Resources"]:
        continue

    department_employees = [
        e for e in employees if e["department"] == department]
    num_leads = max(1, len(department_employees) // EMPLOYEES_PER_LEAD)

    for _ in range(num_leads):
        full_name = faker.name()
        position = random.choice(roles["leads"])
        leads.append({
            "id": lead_id,
            "full_name": full_name,
            "position": position,
            "department": department,
            "career_mentor": "",
            "tech_mentor": "",
            "project": []  # List for multiple project assignments
        })
        lead_id += 1

# Calculate number of department heads needed per department based on LEADS_PER_HEAD
department_heads = []
head_id = lead_id

for department, roles in departments.items():
    # Skip HR and Finance for head generation
    if department in ["Finance", "Human Resources"]:
        continue

    department_leads = [
        lead for lead in leads if lead["department"] == department]
    num_heads = max(1, len(department_leads) // LEADS_PER_HEAD)

    for _ in range(num_heads):
        full_name = faker.name()
        department_heads.append({
            "id": head_id,
            "full_name": full_name,
            "position": f"Department Head",
            "department": department,
            # All department heads report to the CEO
            "career_mentor": CEO["full_name"],
            "tech_mentor": CEO["full_name"],
            "project": []  # List for multiple project assignments
        })
        head_id += 1

# Function to distribute projects evenly among department heads


def distribute_projects_among_heads(projects, heads):
    random.shuffle(projects)  # Shuffle projects to make it random
    for i, project in enumerate(projects):
        head = heads[i % len(heads)]  # Round-robin distribution of projects
        head["project"].append(project)

# Function to assign projects randomly to leads and employees


def assign_projects_randomly(projects, leads, employees):
    all_assignees = leads + employees
    random.shuffle(all_assignees)  # Shuffle to randomize assignment

    # Assign each project equally across assignees, but in random order
    for i, assignee in enumerate(all_assignees):
        project = projects[i % len(projects)]
        assignee["project"].append(project)

# Assign additional projects to some leads and employees (e.g., 20% of them)


def assign_additional_projects(projects, assignees, percentage=0.2):
    num_additional_assignees = int(len(assignees) * percentage)
    selected_assignees = random.sample(assignees, num_additional_assignees)

    for assignee in selected_assignees:
        extra_project = random.choice(projects)
        if extra_project not in assignee["project"]:
            assignee["project"].append(extra_project)


# Distribute projects evenly among department heads
for department, roles in departments.items():
    if department in ["Finance", "Human Resources"]:
        continue

    department_projects = cross_department_projects.copy()
    department_heads_in_dept = [
        head for head in department_heads if head["department"] == department]

    if department_heads_in_dept:
        distribute_projects_among_heads(
            department_projects, department_heads_in_dept)

# Randomly assign projects to leads and employees
assign_projects_randomly(cross_department_projects, leads, employees)

# Assign additional projects to some leads and employees
assign_additional_projects(cross_department_projects,
                           leads + employees, percentage=0.2)

# Function to find a mentor in the same department


def find_department_mentor(employee, mentor_type="career"):
    if employee["position"] in departments[employee["department"]]["employees"]:
        # Regular employees are mentored by leads in the same department
        possible_mentors = [
            lead for lead in leads if lead["department"] == employee["department"]]
    else:
        # Leads are mentored by department heads
        possible_mentors = [
            head for head in department_heads if head["department"] == employee["department"]]

    return random.choice(possible_mentors) if possible_mentors else None


# Assign career and tech mentors to regular employees and leads
for employee in employees + leads:
    career_mentor = find_department_mentor(employee, "career")
    tech_mentor = find_department_mentor(employee, "tech")

    if career_mentor:
        employee["career_mentor"] = career_mentor["full_name"]
    if tech_mentor:
        employee["tech_mentor"] = tech_mentor["full_name"]

# Writing to CSV file
all_employees = [CEO] + department_heads + leads + employees

with open("src/data/employees_with_multiple_projects.csv", mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=[
                            "id", "full_name", "position", "department", "career_mentor", "tech_mentor", "project"])
    writer.writeheader()
    writer.writerows(all_employees)

print("CSV file generated as employees_with_multiple_projects.csv")
