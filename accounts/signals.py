from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    """
    Signal receiver that handles the creation and saving of a UserProfile instance
    whenever a User instance is created or updated.

    Args:
        sender (Model class): The model class that sent the signal (User in this case).
        instance (User): The instance of the model that just got saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.

    Side Effects:
        - If a new User instance is created, a corresponding UserProfile instance is also created.
        - If an existing User instance is saved, it attempts to save the associated UserProfile instance.
        - If the UserProfile instance does not exist during update, it creates a new UserProfile instance.

    Example:
        When a new user is registered:
        >>> user = User.objects.create(...)
        >>> # The above action triggers this signal and creates a UserProfile instance.

        When an existing user is updated:
        >>> user.save()
        >>> # The above action triggers this signal and attempts to save the associated UserProfile.
    """
    print(created)
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            # Create the user profile if it does not exist
            UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    """
    Signal receiver that is triggered before a User instance is saved.

    Args:
        sender (Model class): The model class that sent the signal (User in this case).
        instance (User): The instance of the model that is about to be saved.
        **kwargs: Additional keyword arguments.

    Note:
        Currently, this function does not perform any actions. It serves as a placeholder for
        any pre-save logic that might be added in the future.

    Example:
        Before a user is saved:
        >>> user.save()
        >>> # This signal is triggered before the user instance is actually saved.
    """
    pass

# post_save.connect(post_save_create_profile_receiver, sender=User)