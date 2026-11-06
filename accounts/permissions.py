from .models import User


def is_admin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.role == User.Role.ADMIN
        )
    )


def is_manager(user):
    return (
        user.is_authenticated
        and user.role == User.Role.MANAGER
    )




def can_access_project(user, project):

    if is_admin(user):
        return True

    if user.role == User.Role.MANAGER:
        return project.manager_id == user.id

    if user.role == User.Role.CLIENT:
        return project.client_id == user.id

    return False



def can_access_task(user, task):

    if is_admin(user):
        return True

    if user.role == User.Role.MANAGER:
        return task.project.manager_id == user.id

    if user.role == User.Role.EMPLOYEE:
        return task.assigned_to_id == user.id

    if user.role == User.Role.CLIENT:
        return task.project.client_id == user.id

    return False


def can_manage_task(user, task):

    if is_admin(user):
        return True

    return (
        user.role == User.Role.MANAGER
        and task.project.manager_id == user.id
    )
