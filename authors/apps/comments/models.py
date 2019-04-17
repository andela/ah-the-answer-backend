from django.db import models
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article


class Comment(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    body = models.TextField()
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        related_name="comments",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.body[:15] + "..."

    class Meta:
        ordering = ["-createdAt"]


class LikeDislikeComment(models.Model):
    """
    Class handles liking and dislike of a comment.
    """
    user = models.ForeignKey(
        User,
        related_name='like_by',
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        Comment,
        related_name='liked_comment',
        on_delete=models.CASCADE
    )
    likes = models.IntegerField(null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def react_to_comment(user, comment, value):
        """
        Handles the liking and disliking of a comment
        :param user: instance of the user
        :param comment: instance of the like/dislike comment
        :param value: user reaction,an integer
        :return: exits on success
        """

        user_reaction = LikeDislikeComment.objects.filter(
            user=user,
            comment=comment
        ).values('likes', )
        # if user had not previously like the comment, we mark it as liked
        if len(user_reaction) == 0:
            LikeDislikeComment.objects.create(
                user=user,
                comment=comment,
                likes=value
            )
            return True
        # if the like field already has a matching value to the one in the
        # table, treat that request as reverting the initial value and remove
        # from liking
        elif user_reaction[0]['likes'] == value:
            LikeDislikeComment.objects.filter(
                user=user,
                comment=comment).delete()
            return False
        # if 'likes' field is not empty and the character doesn't match
        # the value provided, that row is deleted and a new instance is
        # created with the new reaction to the article
        new_reaction = LikeDislikeComment.objects.filter(
            user=user,
            comment=comment)
        new_reaction.update(likes=value)
        return True

    @staticmethod
    def get_count_like(comment):
        return LikeDislikeComment.objects.filter(comment=comment,
                                                 likes=1).count()

    @staticmethod
    def get_count_dislike(comment):
        return LikeDislikeComment.objects.filter(comment=comment,
                                                 likes=0).count()

    class Meta:
        ordering = ('-date_created',)
