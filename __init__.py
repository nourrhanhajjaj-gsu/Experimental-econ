from otree.api import *


doc = """
Rochambeau (Rock,Paper,Scissors) Project
"""


class C(BaseConstants):
    NAME_IN_URL = "rochambeau_project"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3

    CHOICES = ["Rock", "Paper", "Scissors"]

    WIN_PAYOFF = cu(100)
    TIE_PAYOFF = cu(0)
    LOSE_PAYOFF = cu(0)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    def set_payoffs(group):
        p1, p2 = group.get_players()

        c1 = p1.choice
        c2 = p2.choice

        if c1 == c2:
            p1.payoff = C.TIE_PAYOFF
            p2.payoff = C.TIE_PAYOFF
            p1.round_result = "You tied with your opponent"
            p2.round_result = "You tied with your opponent"

        elif (c1 == "Rock" and c2 == "Scissors") or \
                (c1 == "Paper" and c2 == "Rock") or \
                (c1 == "Scissors" and c2 == "Paper"):

            p1.payoff = C.WIN_PAYOFF
            p2.payoff = C.LOSE_PAYOFF
            p1.round_result = "You Won this round!"
            p2.round_result = "You Lost this round!"

        else:
            p1.payoff = C.LOSE_PAYOFF
            p2.payoff = C.WIN_PAYOFF
            p1.round_result = "You Lost this round!"
            p2.round_result = "You Won this round!"


class Player(BasePlayer):
    choice = models.StringField(
        choices=C.CHOICES,
        blank=False,
    )
    round_result = models.StringField(blank=True)

    def opponent(player):
        return player.get_others_in_group()[0]


# PAGES
class Play(Page):
    form_model = "player"
    form_fields = ["choice"]

    def vars_for_template(player):
        return dict(
            round_num=player.round_number,
            total_rounds=C.NUM_ROUNDS,
        )


class WaitResults(WaitPage):
    after_all_players_arrive = Group.set_payoffs

    def vars_for_template(player):
        return dict(
            round_num=player.round_number,
            total_rounds=C.NUM_ROUNDS,
        )


class Results(Page):
    def vars_for_template(player):
        opp = player.opponent()
        return dict(
            round_num=player.round_number,
            total_rounds=C.NUM_ROUNDS,
            my_choice=player.choice,
            opp_choice=opp.choice,
            my_result=player.round_result,
            my_round_payoff=player.payoff,
            my_total_payoff=sum(p.payoff for p in player.in_all_rounds()),
        )


class FinalResults(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player):
        rounds = []
        total = cu(0)
        wins = ties = losses = 0

        for p in player.in_all_rounds():
            opp = p.opponent()
            total += p.payoff
            if p.round_result == "You Won this round!":
                wins += 1
            elif p.round_result == "You tied with your opponent":
                ties += 1
            else:
                losses += 1

            rounds.append(
                dict(
                    round_number=p.round_number,
                    my_choice=p.choice,
                    opp_choice=opp.choice,
                    result=p.round_result,
                    payoff=p.payoff,
                )
            )

        return dict(
            total_payoff=total,
            wins=wins,
            ties=ties,
            losses=losses,
            rounds=rounds,
            total_rounds=C.NUM_ROUNDS,
        )


page_sequence = [Play, WaitResults, Results, FinalResults]