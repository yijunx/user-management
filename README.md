# user-management




# rbac of user-management
* When a user logs in with google or wechat, a user will be created in the db.
* a user admin can
  * ban a user
  * create/remove/list/patch user roles in other services and this service
* policies:

    p, user_admin_role_id, users, manage  # added from beginning

    (where manage is a right, which contains actions like make_admin/remove_admin/list_admin )

* groupings:

    g, a_user_admin_user_id, user_admin_role_id  # added from beginning