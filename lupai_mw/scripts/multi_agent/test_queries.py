import regex

from typing import Annotated
from pydantic import BaseModel, StrictStr, field_validator, AfterValidator


def remove_extra_spaces(text: str) -> str:
    return regex.sub(r"\p{White_Space}{2,}", " ", text)


Answer = Annotated[
    str,
    AfterValidator(remove_extra_spaces),
]


class Translations(BaseModel):
    query: StrictStr
    expected_answer: Answer


class TestQuery(BaseModel):
    query: StrictStr
    expected_answer: Answer
    expected_sources: list[StrictStr]
    translations: Translations

    @field_validator("expected_sources", mode="after")
    @classmethod
    def expected_sources_validator(cls, v: list[str]) -> list[str]:
        return sorted(v)


test_queries = [
    TestQuery(
        query="Meine Schüler sind unmotiviert. Was kann ich tun?",
        expected_answer="""Paraphrase Handbuch-Kapitel 3.1 Motivation
        (Pimp my School-Handbuch MV https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf)""",
        expected_sources=[
            "https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf",
            "https://meinsvwissen.de/motivation/",
        ],
        translations=Translations(
            query="My students are unmotivated. What can I do?",
            expected_answer="""Paraphrase of Handbook Chapter 3.1:
            Motivation (Pimp my School Handbook MV – https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf)""",
        ),
    ),
    TestQuery(
        query="Unsere Schulleitung verbietet uns einen instagram-Account für die SV zu gründen. Ist das legal?",
        expected_answer="""Nein. Paragraph zu Schülerzeitung aus dem jeweiligen Schulgesetz aus dem Bundesland muss verwiesen werden.
        Instagram lässt sich argumentieren als moderne Schülerzeitung, weil es grundsätzlich um Medien von Schüler:innen geht.
        Wichtig: muss im Namen der SV sein, nicht im Namen der Schule.
        Vorgehensweise: § da haben, Gespräch suchen, ggf. muss Schulaufsicht mit ins Boot geholt werden, ggf.
        viele verschiedene Beispiele von anderen Schulen parat haben.""",
        expected_sources=[
            "https://meinsvwissen.de/instagram/",
        ],
        translations=Translations(
            query="Our school administration forbids us from creating an Instagram account for the student council. Is that legal?",
            expected_answer="""No. Reference must be made to the paragraph on student newspapers from the respective state school law.
            Instagram can be argued to be a modern form of a student newspaper, since it is essentially about media created by students.
            Important: it has to be in the name of the student council, not in the name of the school.
            Procedure: have the legal paragraph at hand, seek a conversation, if necessary involve the school supervisory authority,
            and if needed, have many different examples from other schools ready.""",
        ),
    ),
    TestQuery(
        query="Wie wird die Wahl von Schulsprecher:innen organisiert?",
        expected_answer="""verschiedene Optionen vorstellen: Vollversammlung + Vor- und Nachteile, Wahl im Schülerrat + Vor- und Nachteile,
        Tipps: richtigen Wahlkampf der Kandidat:innen organisieren
        (Handbuch Pimp my School MV Kapitel 2.1.2 SV-Vorstand https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf)
        wichtig: jedes Bundesland hat andere rechtliche Vorgaben dafür, wer gewählt werden kann und wer stimmberechtigt ist""",
        expected_sources=[
            "https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf",
        ],
        translations=Translations(
            query="How is the election of student representatives organized?",
            expected_answer="""Present different options: general assembly + pros and cons, election within the student council + pros and cons.
            Tips: organize a proper election campaign for the candidates.
            (Handbook Pimp my School MV Chapter 2.1.2 Student Council Executive Board https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf)
            Important: each federal state has different legal regulations regarding who can be elected and who is eligible to vote.""",
        ),
    ),
    TestQuery(
        query="Dürfen Klassensprecher:innen von Lehrer:innen abgesetzt werden?",
        expected_answer="""Nein, jeweils konkreter Paragraph aus dem Schulgesetz.
        Meist so etwas wie: Dass jeweils nur das Gremium selbst absetzen kann, in dem Fall die Klasse selbst.
        Vorgehensweise empfehlen: Evaluation mit der Klasse gemeinsam, ob Klassensprecher:innen geeignet sind. Z.B.
        mit Evaluationsbogen aus der Broschüre Wahlen oder offenes Gespräch, dann ggf. Neuwahl - Vorgehensweise also:
        die Wähler:innen müssen sich eine neue Meinung bilden, wenn z.B. etwas vorgefallen ist und dann kann neu gewählt werden.""",
        expected_sources=[],
        translations=Translations(
            query="Are class representatives allowed to be removed from office by teachers?",
            expected_answer="""No, the relevant paragraph from the school law must be cited.
            Usually, it states something like: only the body itself can remove its representatives, in this case the class itself.
            Recommended procedure: conduct an evaluation together with the class to determine whether the class representatives are suitable.
            For example, use an evaluation form from the Wahlen brochure or hold an open discussion.
            If necessary, then organize a new election — in other words, the voters must form a new opinion if, for example,
            something has happened, and then a new vote can be held.""",
        ),
    ),
    TestQuery(
        query="Wie bereite ich einen Projekttag für die SV sinnvoll vor? Methoden, Ablaufplan, Vorbereitung",
        expected_answer="""Paraphrase aus Handbuch Pimp my School MV Kapitel 2.2
        eien Auftaktveranstaltung durchführen https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf""",
        expected_sources=[
            "https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf",
            "https://meinsvwissen.de/seminare-gestalten/",
        ],
        translations=Translations(
            query="How do I prepare a project day for the student council in a meaningful way? Methods, schedule, preparation",
            expected_answer="""Paraphrase from Pimp my School MV Handbook, Chapter 2.2:
            hold a kickoff event https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf""",
        ),
    ),
    TestQuery(
        query="Woher kriegen wir Geld für die SV-Arbeit?",
        expected_answer="""SV-Handbuch Finanzierungsmöglichkeiten - allerdings ist die Seite im jeweiligen Handbuch (NRW; Berlin, MV)
        jeweils für das jeweilige BuLa geschrieben. Es gibt die Eigenfinanzierungsseite, die jeweils für alle gilt - die Antwort müsste so etwas sein,
        dass es wenig Antragsmöglichkeiten gibt - das ist dann die jeweilige BuLä-spezifische Seite. Und:
        dass dann immer angeraten wird Eigenfinanzierung aufzubauen - dann jeweils 3 niedrigschwellige
        Arten auflisten von der FinanzierungsEigenmittelSeite aus dem Handbuch Pimp my
        School MV S.112-113 https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf
        . Und ggf. nachfragen wieviel Geld gebraucht wird und dann 2-3 Vorschläge machen, die jeweils mit der Größenordnung passen.
        In NRW kann z.B. in manchen Kreisen Geld beantragt werden - steht dann auch auf der jeweiligen Seite des Handbuchs des Bundeslands.""",
        expected_sources=[
            "https://library.fes.de/pdf-files/bueros/schwerin/20577.pdf",
        ],
        translations=Translations(
            query="Where can we get money for student council work?",
            expected_answer="""Student council handbook on funding options – however, the page in each handbook (NRW; Berlin; MV)
            is written specifically for that federal state.
            There is a section on self-financing, which applies to all – so the answer should point out that
            there are few application-based funding opportunities, and those are specific to each state.
            It is always recommended to build up self-financing.
            For that, three low-threshold options are listed in the Pimp my School MV handbook (pp. 112–113):
            Collecting membership fees or voluntary contributions from students.
            Organizing fundraising activities such as bake sales, flea markets, or small events.
            Cooperating with local partners or sponsors (e.g. shops or associations).
            It may also be useful to ask how much money is needed and then suggest 2–3 options that match the scale of the project.
            In NRW, for example, in some districts it is possible to apply for funds – this is also listed on the respective federal state’s handbook page.""",
        ),
    ),
    TestQuery(
        query="Welche Rechte haben Schüler:innen?",
        expected_answer="""Antwort aus dem jeweiligen Schulgesetz in verständlicher Sprache""",
        expected_sources=[],
        translations=Translations(
            query="What rights do students have?",
            expected_answer="""Answer from the respective school law, explained in plain language.""",
        ),
    ),
    TestQuery(
        query="Was gibt es für coole SV-Projekte?",
        expected_answer="""Auswahl zu verschiedenen Themenbereichen aus dem Handbuch Pimp my School oder den Webseiten mit Projektideen""",
        expected_sources=[],
        translations=Translations(
            query="What cool student council projects are there?",
            expected_answer="""A selection of different topic areas from the Pimp my School handbook or from websites with project ideas.""",
        ),
    ),
    TestQuery(
        query="Wir hätten gern ein SV-Seminar an der Schule. Wen können wir dazu anfragen?",
        expected_answer="""Dokument:
        Seminaranbieter https://meinsvwissen.de/download/62/1-7-unterstuetzung/8716/seminaranbieter-fuer-workshops-projekttage-und-sv-fahrten-2.pdf""",
        expected_sources=[
            "https://meinsvwissen.de/download/62/1-7-unterstuetzung/8716/seminaranbieter-fuer-workshops-projekttage-und-sv-fahrten-2.pdf"
        ],
        translations=Translations(
            query="We would like to have a student council seminar at our school. Who can we contact for that?",
            expected_answer="""Document:
            Seminar providers https://meinsvwissen.de/download/62/1-7-unterstuetzung/8716/seminaranbieter-fuer-workshops-projekttage-und-sv-fahrten-2.pdf""",
        ),
    ),
    TestQuery(
        query="Nazis sind ein Problem bei uns. Was können wir als SV dagegen tun?",
        expected_answer="""Rechtsextremismus bedroht Demokratie und Zusammenhalt.
        Als Schülervertretung (SV) könnt ihr viel tun – zeigt Haltung, schützt Betroffene und organisiert Unterstützung.

        1. Sichtbar Haltung zeigen Formuliert ein klares Statement, z. B. bei der nächsten Schulversammlung oder per Aushang:
            An unserer Schule ist kein Platz für Rassismus, Antisemitismus oder rechtsextreme Hetze. Wir stehen für Respekt, Vielfalt und Demokratie.“
            Schülervertretung (SV) kann Stellungnahmen veröffentlichen. Plant Aktionen wie Plakatkampagnen, Gedenktage oder Friedenswochen.
            Solche Signale stärken alle, die betroffen oder verunsichert sind.

        2. Betroffene schützen, Allianzen bilden
            Sprecht mit Betroffenen, zeigt Solidarität, hört zu.
            Bündnisse mit engagierten Lehrkräften, Schulsozialarbeit, Eltern, Schüler:innen bilden
            Nutzt bestehende Gremien wie Klassenrat oder Schulkonferenz für demokratische Beschlüsse.
            Wenn jemand bedroht oder verletzt wird: Anzeige erstatten, Jugendamt oder Polizei informieren.

        3. Dokumentieren & Beobachten
            Gewalt, Hassreden, Symbole (z. B. Hakenkreuze), Drohungen o. Ä. sollten dokumentiert (Datum, Ort, Zeugen) und ggf.
            fotografiert werden – aber ohne euch selbst in Gefahr zu bringen.
            Verhalten protokollieren: Wer macht was, wann, in welchem Kontext?

        4. Verbindliche Prozesse anstoßen
            Meldet rechtsextreme Vorfälle an Vertrauenslehrer:innen, Schulsozialarbeit oder Schulleitung.
            Prüft gemeinsam, welche schulischen oder rechtlichen Schritte möglich sind (Gespräche, Ordnungsmaßnahmen etc.).
            Wenn intern nichts passiert oder vertuscht wird, kontaktiert Schulaufsicht, GEW oder Landesschülervertretung.
            In schweren Fällen: Schulpsychologie oder externe Beratungsstellen einschalten.

        5. Information & Aufklärung
            Organisiert Projekte und Workshops zu Demokratie und Vielfalt, z. B.:
            Zeitzeugengespräche, Filmabende, Antirassismus-Trainings, Theaterprojekte, Schulkinowochen, Argumentationstrainings gegen rechte Parolen
            Arbeitet mit Initiativen wie RAA Brandenburg, Mobile Beratung gegen Rechtsextremismus, „Schule ohne Rassismus – Schule mit Courage“ zusammen.

        6. Externe Unterstützung nutzen
            Holt euch Fachkräfte von Beratungsstellen, zivilgesellschaftlichen Organisationen oder der Landesschülervertretung.

        7. Langfristige Schulentwicklung fördern
            Setzt euch für eine demokratische Schulkultur ein, wie sie in Projekten wie DEINS! oder EmPa³ erprobt wurde.
            Stärkt Mitbestimmung, Konfliktlösungskompetenzen und verankert Antidiskriminierung strukturell.

        Merkt euch:
        Sprich drüber! Schweigen schützt Täter!
        Handle klug! Aber nicht allein. Hol dir Hilfe.
        Rechtsextremismus ist keine Meinung – sondern ein Angriff auf die Demokratie.""",
        expected_sources=[],
        translations=Translations(
            query="Nazis are a problem at our school. What can we as the student council do about it?",
            expected_answer="""Right-wing extremism threatens democracy and social cohesion.
            As a student council (SV), you can do a lot – take a stand, protect those affected, and organize support.

            1. Take a visible stand
            Formulate a clear statement, for example at the next school assembly or on a notice board:
            “At our school there is no place for racism, antisemitism, or right-wing extremist hate. We stand for respect, diversity, and democracy.”
            The student council can publish statements. Plan actions such as poster campaigns, remembrance days, or peace weeks.
            Such signals strengthen those who are affected or feel insecure.

            2. Protect those affected, build alliances
            Talk to those affected, show solidarity, listen.
            Build alliances with committed teachers, school social workers, parents, and students.
            Use existing bodies such as class councils or the school conference to adopt democratic resolutions.
            If someone is threatened or attacked: file a report, inform child welfare services or the police.

            3. Document & observe
            Incidents of violence, hate speech, symbols (e.g. swastikas), threats, etc. should be documented (date, place, witnesses) and, if safe, photographed – but without putting yourselves at risk.
            Record behavior: who does what, when, and in what context?

            4. Initiate binding processes
            Report right-wing extremist incidents to trusted teachers, school social workers, or the school administration.
            Check together what school or legal steps are possible (conversations, disciplinary measures, etc.).
            If nothing happens internally or incidents are covered up, contact the school supervisory authority, the teachers’ union (GEW), or the state student council.
            In serious cases: involve school psychology services or external counseling centers.

            5. Provide information & education
            Organize projects and workshops on democracy and diversity, such as:

            eyewitness talks,
            film nights,
            anti-racism trainings,
            theater projects,
            school cinema weeks,
            argumentation trainings against right-wing slogans.

            Work with initiatives such as RAA Brandenburg, Mobile Counseling against Right-Wing Extremism, or School without Racism – School with Courage.

            6. Use external support
            Bring in experts from counseling centers, civil society organizations, or the state student council.

            7. Promote long-term school development
            Advocate for a democratic school culture, as tested in projects like DEINS! or EmPa³.
            Strengthen participation, conflict resolution skills, and anchor anti-discrimination structurally.

            Remember:

            Speak up! Silence protects perpetrators.
            Act wisely! But not alone. Get help.
            Right-wing extremism is not an opinion – it is an attack on democracy.
            """,
        ),
    ),
]
