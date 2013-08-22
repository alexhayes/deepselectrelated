# Deep select_related

The purpose of this repo is to show a potential issue of Django's select_related 
queryset method. This maybe perhaps due to the slightly odd schema implementation however
either way the behaviour is unexpected.

I've done my testing on the (as of writing) latest django master (sha c5f768f8cc53a54686bcb1867cc4400393427ffe)

## Issue

When using select_related on a deeply nested relationship and you have two (or possibly more)
relationships that use the same model the SQL query is incorrect and thus
the resulting model incorrect. 

This has been created as [https://code.djangoproject.com/ticket/20955#ticket issue #20955 in Django].

## Example

```python
expect = Task.objects.get(pk=1)
actual = Task.objects.select_related('creator__staffuser__staff', 'owner__staffuser__staff').get(pk=1)

if actual.creator.staffuser.staff != expect.creator.staffuser.staff:
    print "Creator Incorrect"
if actual.owner.staffuser.staff != expect.owner.staffuser.staff:
    print "Owner Incorrect"
```

Outputs ```Owner Incorrect```

## Tests

Running the tests will expose the issue:

```bash
./manage.py test deepselectrelated
```

## Issue Location

It appears that this issue exists in the actual SQL statements that are being 
generated, as follows:

```sql
         SELECT "deepselectrelated_task"."id", "deepselectrelated_task"."title", "deepselectrelated_task"."creator_id", "deepselectrelated_task"."owner_id", 
                "auth_user"."id", "auth_user"."password", "auth_user"."last_login", "auth_user"."is_superuser", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name", "auth_user"."email", "auth_user"."is_staff", "auth_user"."is_active", "auth_user"."date_joined", 
                "deepselectrelated_staffuser"."user_ptr_id", "deepselectrelated_staffuser"."staff_id", 
                "deepselectrelated_staff"."id", "deepselectrelated_staff"."name", 
                T5."id", T5."password", T5."last_login", T5."is_superuser", T5."username", T5."first_name", T5."last_name", T5."email", T5."is_staff", T5."is_active", T5."date_joined", 
                T6."user_ptr_id", T6."staff_id", 
                "deepselectrelated_staff"."id", "deepselectrelated_staff"."name" 
           FROM "deepselectrelated_task" 
     INNER JOIN "auth_user" ON ( "deepselectrelated_task"."creator_id" = "auth_user"."id" ) 
LEFT OUTER JOIN "deepselectrelated_staffuser" ON ( "auth_user"."id" = "deepselectrelated_staffuser"."user_ptr_id" ) 
LEFT OUTER JOIN "deepselectrelated_staff" ON ( "deepselectrelated_staffuser"."staff_id" = "deepselectrelated_staff"."id" ) 
     INNER JOIN "auth_user" T5 ON ( "deepselectrelated_task"."owner_id" = T5."id" ) 
LEFT OUTER JOIN "deepselectrelated_staffuser" T6 ON ( T5."id" = T6."user_ptr_id" )
```

Note that there is only one join to the staff table and the following part of the SELECT query is incorrectly repeated:

```sql
"deepselectrelated_staff"."id", "deepselectrelated_staff"."name"
```

There should infact be two joins to the staff table and the SELECT should be as follows:

```sql
         SELECT "deepselectrelated_task"."id", "deepselectrelated_task"."title", "deepselectrelated_task"."creator_id", "deepselectrelated_task"."owner_id", 
                "auth_user"."id", "auth_user"."password", "auth_user"."last_login", "auth_user"."is_superuser", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name", "auth_user"."email", "auth_user"."is_staff", "auth_user"."is_active", "auth_user"."date_joined", 
                "deepselectrelated_staffuser"."user_ptr_id", "deepselectrelated_staffuser"."staff_id", 
                "deepselectrelated_staff"."id", "deepselectrelated_staff"."name", 
                T5."id", T5."password", T5."last_login", T5."is_superuser", T5."username", T5."first_name", T5."last_name", T5."email", T5."is_staff", T5."is_active", T5."date_joined", 
                T6."user_ptr_id", T6."staff_id", 
                T7."id", T7."name" 
           FROM "deepselectrelated_task" 
     INNER JOIN "auth_user" ON ( "deepselectrelated_task"."creator_id" = "auth_user"."id" ) 
LEFT OUTER JOIN "deepselectrelated_staffuser" ON ( "auth_user"."id" = "deepselectrelated_staffuser"."user_ptr_id" ) 
LEFT OUTER JOIN "deepselectrelated_staff" ON ( "deepselectrelated_staffuser"."staff_id" = "deepselectrelated_staff"."id" ) 
     INNER JOIN "auth_user" T5 ON ( "deepselectrelated_task"."owner_id" = T5."id" ) 
LEFT OUTER JOIN "deepselectrelated_staffuser" T6 ON ( T5."id" = T6."user_ptr_id" )
LEFT OUTER JOIN "deepselectrelated_staff" T7 ON ( T6."staff_id" = T7."id" )
```