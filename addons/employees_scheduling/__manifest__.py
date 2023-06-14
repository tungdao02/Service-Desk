{
    "name": "Employees Scheduling",
    "version": "1.0",
    "depends": ["base", "hr"],
    "author": "Pham Minh Duc",
    "category": "Human Resources",
    "description": """
    Description text
    """,
    # data files always loaded at installation
    "data": [
        "security/ir.model.access.csv",
        "views/employees_scheduling_view.xml",
        "views/shifts_views.xml",
        "views/employee_schedule_report_view.xml",
        
    ],
    "assets": {
        "web.assets_backend": [
            "employees_scheduling/static/src/scss/schedule.scss",
            "employees_scheduling/static/src/js/employee_schedule_report.js",
        ],
    },
    "installable": True,
    "application": True,
}
