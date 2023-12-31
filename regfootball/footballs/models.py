from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.template.defaultfilters import slugify
from django.urls import reverse


def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))


class Rounds(models.Model):
    round = models.CharField(max_length=12, unique=True, verbose_name="Тур / стадія плей-оф")

    def __str__(self):
        return f'{self.round}'

    class Meta:
        verbose_name = "Раунд"
        verbose_name_plural = "Раунди"


class Regions(models.Model):
    name = models.CharField(max_length=100, blank=True, verbose_name="Область", unique=True)
    region_slug = models.SlugField(max_length=70, unique=True, db_index=True, verbose_name="Slug")
    date_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} область'

    class Meta:
        verbose_name = "Область"
        verbose_name_plural = "Області"


class Tournaments(models.Model):
    tournament_slug = models.SlugField(max_length=250, unique=True, db_index=True, verbose_name="Slug")
    name = models.CharField(max_length=150, verbose_name="Назва турніру", unique=True)
    full_name = models.CharField(max_length=350, verbose_name="Повна назва турніру")
    region = models.ForeignKey(Regions, on_delete=models.DO_NOTHING, verbose_name="Область")
    description = models.TextField(blank=True, verbose_name="Опис")
    link = models.URLField(blank=True, verbose_name="посилання на офіційний сайт")
    logotype = models.ImageField(upload_to='footballs/static/footballs/img/logo_tournaments/', verbose_name="Логотип",
                                 blank=True, default='footballs/static/footballs/img/logo_teams/Снимок.PNG')
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    objects = models.Manager

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Турнір"
        verbose_name_plural = "Турніри"

    def get_absolute_url(self):
        return reverse('footballs:tournament_info', kwargs={'tournament_slug': self.tournament_slug})


class Teams(models.Model):
    team_slug = models.SlugField(max_length=250, unique=True, db_index=True, verbose_name="Slug")
    team = models.CharField(max_length=80, verbose_name="Назва команди")
    team_full_name = models.CharField(max_length=200, blank=True, verbose_name="Повна назва")
    region = models.ForeignKey(Regions, on_delete=models.DO_NOTHING, verbose_name="Область")
    town = models.CharField(max_length=100, blank=True, verbose_name="Місто")
    address = models.CharField(max_length=350, blank=True, verbose_name="Адреса клубу/команди")
    link = models.URLField(blank=True, verbose_name="посилання на офіційний сайт")
    description = models.TextField(blank=True, verbose_name="Опис")
    logotype = models.ImageField(upload_to="footballs/static/footballs/img/logo_teams/",
                                 verbose_name="Логотип",
                                 blank=True,
                                 null=True)
    # , default='footballs/static/footballs/img/logo_teams/Снимок.PNG')
    born = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1940)],
                               verbose_name="Рік заснування")
    stadium = models.CharField(max_length=50, blank=True, verbose_name="Домашній стадіон")
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    objects = models.Manager

    def __str__(self):
        return self.team

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команди"

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.team)
    #     super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('footballs:team', kwargs={'team_slug': self.team_slug})

    def save(self, *args, **kwargs):
        self.team_slug = slugify(translit_to_eng(self.team))
        super().save(*args, **kwargs)


class TournamentTables(models.Model):
    region = models.ForeignKey(Regions, on_delete=models.PROTECT, verbose_name="Область")
    tournament = models.ForeignKey(Tournaments, on_delete=models.PROTECT, verbose_name="Назва турніру")
    season = models.CharField(max_length=10, verbose_name='Сезон')
    team = models.ManyToManyField(Teams, related_name='teams', verbose_name="Команди")
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.region} - {self.tournament} {self.season}'

    class Meta:
        verbose_name = "Турнірна таблиця сезону"
        verbose_name_plural = "Турнірні таблиці сезону"

    def get_absolute_url(self):
        return reverse('footballs:tournament', kwargs={
            'region_slug': self.region.region_slug,
            'tournament_slug': self.tournament.tournament_slug,
            'season_year': self.season,
        })


class Matches(models.Model):
    STATUS_MATCH = (
        ('not_played', 'Не зіграно'),
        ('played', 'Зіграно'),
        ('tech_defeat', 'Тех. поразка'),
    )

    match_date = models.DateField(blank=True, default='01.01.2023', verbose_name="Дата")
    match_time = models.TimeField(blank=True, default='00:00', verbose_name="Час")
    tournament = models.ForeignKey(Tournaments, on_delete=models.DO_NOTHING, related_name='tournaments',
                                      verbose_name="Турнір")
    host_team = models.ForeignKey(Teams, on_delete=models.DO_NOTHING, related_name="teams_home",
                                     verbose_name="Команда господар")
    visiting_team = models.ForeignKey(Teams, on_delete=models.DO_NOTHING, related_name="teams_guests",
                                         verbose_name="Команда гостей")
    host_team_goals = models.IntegerField(null=True, blank=True, verbose_name="Забити голи - господарі",
                                          validators=[MinValueValidator(0),
                                                      MaxValueValidator(99)])
    visiting_team_goals = models.IntegerField(null=True, blank=True, verbose_name="Забити голи - гості",
                                              validators=[MinValueValidator(0),
                                                          MaxValueValidator(99)])
    status = models.CharField(max_length=11, choices=STATUS_MATCH, blank=True, default='not_played',
                              verbose_name="Статус")
    round = models.ForeignKey(Rounds, on_delete=models.DO_NOTHING, related_name='tur', verbose_name="Тур")
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tournament} |{self.round} | {self.host_team} {self.host_team_goals}:{self.visiting_team_goals} {self.visiting_team} | {self.status}'

    class Meta:
        verbose_name = "Матчі"
        verbose_name_plural = "Матчі"
