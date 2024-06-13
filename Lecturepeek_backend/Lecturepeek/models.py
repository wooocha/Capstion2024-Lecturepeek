from django.db import models


class Video(models.Model):
    video_id = models.CharField(max_length=255)
    creation_type = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.video_id} - {self.creation_type}"


class SummaryNote(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='summary_notes')
    timestamp = models.CharField(max_length=255)
    section_title = models.CharField(max_length=255)
    content = models.TextField()


    def __str__(self):
        return f"{self.section_title} - {self.timestamp}"


class Script(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='scripts')
    timestamp = models.CharField(max_length=255)
    content = models.TextField()


    def __str__(self):
        return f"{self.timestamp} - Script"


class Test(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='problems')
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return f"Question: {self.question[:50]}... - Answer: {self.answer[:50]}..."
