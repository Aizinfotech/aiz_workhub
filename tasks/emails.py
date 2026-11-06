from django.core.mail import send_mail


def send_task_assignment_email(task):

    if not task.assigned_to:
        return

    if not task.assigned_to.email:
        return

    send_mail(
        subject=f"New Task Assigned: {task.title}",
        message=(
            f"Project: {task.project}\n"
            f"Task: {task.title}\n"
            f"Status: {task.get_status_display()}\n"
            f"Priority: {task.get_priority_display()}\n"
            f"Due Date: {task.due_date or '-'}"
        ),
        from_email=None,
        recipient_list=[task.assigned_to.email],
    )



def send_task_status_email(task):

    if not task.assigned_to:
        return

    if not task.assigned_to.email:
        return

    send_mail(
        subject=f"Task Status Updated: {task.title}",
        message=(
            f"Task: {task.title}\n"
            f"New Status: "
            f"{task.get_status_display()}"
        ),
        from_email=None,
        recipient_list=[task.assigned_to.email],
    )
