// „So entsteht diese Seite“: der Weg einer Information von der Quelle bis zur
// Anzeige. Alle Zahlen kommen aus dem Bestand, keine steht fest im Text —
// sonst veraltet die Erklärung schneller als das, was sie erklärt.
import {
  bestand, sessionRegister, votenVon, tierCounts, votes, bodyMap, sessionMap,
} from "../daten.js";
import { backLink } from "../routing.js";
import { html, roh } from "../html.js";
import { monatJahr } from "./diagramme.js";

const main = document.getElementById("main");

// Die Stufen in der Reihenfolge des Balkens, von der sichersten zur
// dünnsten. Die Schlüssel sind die der Datenlage und stehen in deren Adressen.
const STUFEN = [
  { key: "explicit", titel: "Namentlich in der Niederschrift",
    was: "Der Rat hat namentlich abgestimmt, die Niederschrift nennt jede Stimme. Der sicherste Fall, und der seltenste." },
  { key: "implicit", titel: "Aus der Anwesenheit abgeleitet",
    was: "Das Ergebnis war einstimmig. Wer laut Anwesenheitsliste da war, hat so gestimmt." },
  { key: "tracked", titel: "Im Saal mitgeschrieben",
    was: "Während der Sitzung erfasst. Dabei steht, wer mitgeschrieben hat und ob die Presse dasselbe berichtet." },
  { key: "press", titel: "Aus der Presse",
    was: "Ein Zeitungsartikel nennt die Gegenstimmen und steht bei der Abstimmung." },
  { key: "selbstauskunft", titel: "Aus eigenen Notizen rekonstruiert",
    was: "Ein Ratsmitglied hat aus seinen Notizen ergänzt, auch über andere Mitglieder." },
  { key: "sum", titel: "Nur das Ergebnis",
    was: "Bekannt sind nur die Zahlen. Bei allen Mitgliedern steht ein Fragezeichen, auch wo eine Vermutung nahe läge." },
];

// Die Erklärtexte zu den Kästen des Prozessbilds.
const ERKLAERUNG = {
  niederschrift: {
    titel: "Niederschrift",
    absaetze: [
      "Das amtliche Protokoll einer Sitzung. Die Stadt veröffentlicht es als PDF, nachdem der Rat es in einer späteren Sitzung genehmigt hat. Darin stehen Tagesordnung, Beschlusswortlaut, das Ergebnis als Zahlen und die Anwesenheit. Namen zu einzelnen Stimmen nur dann, wenn der Rat namentlich abgestimmt hat.",
      "Das PDF bleibt bei jeder Sitzung verlinkt. Wo diese Seite und die Niederschrift auseinandergehen, gilt die Niederschrift.",
    ],
  },
  auszug: {
    titel: "Beschlussauszug",
    absaetze: [
      "Für manche Ausschusssitzungen veröffentlicht die Stadt keine Niederschrift, sondern nur die Beschlüsse als Webseite: Tagesordnung, Beschluss, Stimmenzahlen — ohne Anwesenheitsliste.",
      "Weil niemand weiß, wer gefehlt hat, lässt sich Stimmverhalten nur ableiten, wenn alle Sitze mitgestimmt haben.",
    ],
  },
  mitschrift: {
    titel: "Mitschrift im Saal",
    absaetze: [
      "Während der öffentlichen Sitzung hält eine Person im Saal fest, wer wie stimmt. Bei jeder so erfassten Abstimmung steht, wer mitgeschrieben hat.",
      "Sie ergänzt die Niederschrift um die Einzelstimmen, sie ersetzt sie nicht: übertragen wird erst, wenn die Niederschrift vorliegt, und Titel wie Reihenfolge kommen von dort.",
    ],
  },
  presse: {
    titel: "Presse",
    absaetze: [
      "Lokalzeitungen nennen oft einzelne Gegenstimmen, die in der Niederschrift fehlen. Ein Skript durchsucht Artikel aus den Tagen nach einer Sitzung nach den wenigen Wendungen, mit denen Zeitungen das schreiben — „gegen die Stimmen von“, „einzige Gegenstimme“ — und legt den Satz dazu, in dem der Name steht.",
      "Eingetragen wird davon nichts. Übernommen wird, was ein Mensch am Artikel geprüft hat; der Artikel steht dann bei der Abstimmung.",
    ],
  },
  notizen: {
    titel: "Eigene Notizen von Ratsmitgliedern",
    absaetze: [
      "Wo Stimmen offen bleiben, können Ratsmitglieder aus eigenen Notizen ergänzen, auch über andere Mitglieder. Ein Skript stellt je Person die Liste ihrer offenen Abstimmungen zusammen; eingetragen wird, wie abgestimmt wurde oder dass die Erinnerung fehlt.",
      "Solche Angaben heißen „aus eigenen Notizen rekonstruiert“ und sind an jeder Stimme erkennbar. Auch sie warten auf die Niederschrift.",
    ],
  },
  ableiten: {
    titel: "Rechenregeln und Prüfung",
    absaetze: [
      "Alle Quellen laufen durch dieselben Schritte. Es sind Rechenregeln ohne Ermessen: gleich bei jeder Änderung, gleich für jedes Mitglied, nachlesbar im Quellcode. Im Einzelnen stehen sie unten unter „Woher die Einzelstimmen stammen“.",
      "Danach prüft ein Skript Form und Zusammenhang aller Dateien. Erst wenn das aufgeht, gibt ein Mensch frei.",
    ],
  },
  bestand: {
    titel: "Öffentliche Dateien",
    absaetze: [
      "Der Bestand liegt in neun Dateien in einem öffentlichen Git-Repository. Git hält jede Änderung mit Datum fest, jede Korrektur bleibt rückverfolgbar.",
      "Ihr Browser lädt diese Dateien und rechnet die Anzeige selbst aus. Dabei läuft kein Sprachmodell: alles, was Sie sehen, steht vorher geprüft in den Dateien.",
    ],
  },
};

// Wie viele Abstimmungen stammen aus Sitzungen dieser Stufe? Die Gesamtzahl
// taugt dafuer nicht: ein Teil kommt aus Beschlussauszuegen.
const ausStufe = stufe =>
  votes.filter(v => (sessionMap[v.sessionId] || {}).niederschrift === stufe).length;

// Wie viele Abstimmungen tragen mindestens einen Ausschluss dieses Grundes?
const mitGrund = grund =>
  votes.filter(v => (v.excluded || []).some(e => e.reason === grund)).length;

// Wie viele Sitzungen sind davon betroffen?
const sitzungenMitGrund = grund =>
  new Set(votes.filter(v => (v.excluded || []).some(e => e.reason === grund))
               .map(v => v.sessionId)).size;

// Die Zahl der Sitze eines Gremiums heute — nicht fest eintragen, die
// Ausschüsse sind 2026 gewachsen.
function sitze(bodyId) {
  const b = bodyMap[bodyId];
  if (!b) return null;
  const cfgs = b.seatConfigs || [];
  const cfg = cfgs.length ? cfgs[cfgs.length - 1] : b;
  return 1 + (cfg.vicechairs || []).length + (cfg.seats || []).length;
}

const prozent = (teil, ganz) => ganz ? Math.round(teil / ganz * 100) : 0;
const zahl = n => n.toLocaleString("de-DE");

// -- Prozessbild --

const QUELLEN = [
  { k: "niederschrift", titel: "Niederschrift", amtlich: true,
    was: "PDF aus dem Ratsinformationssystem, mit Anwesenheitsliste",
    schritte: [
      ["ki", "liest Tagesordnung, Beschlüsse, Stimmenzahlen und Anwesenheit aus dem PDF"],
      ["ki", "schlägt vor, zu welchem Dossier ein Beschluss gehört"],
      ["mensch", "korrigiert Übertragung und Zuordnung und gibt sie frei"],
    ] },
  { k: "auszug", titel: "Beschlussauszug", amtlich: true,
    was: "Textfassung der Stadt, ohne Anwesenheitsliste",
    schritte: [
      ["skript", "liest Tagesordnung, Beschluss und Stimmenzahlen aus dem Auszug"],
      ["mensch", "korrigiert und gibt frei"],
    ] },
  { k: "mitschrift", titel: "Mitschrift im Saal", amtlich: false,
    was: "während der öffentlichen Sitzung erfasst, mit Namen der erfassenden Person",
    schritte: [
      ["mensch", "überträgt die Einzelstimmen, sobald die Niederschrift vorliegt"],
    ] },
  { k: "presse", titel: "Presse", amtlich: false,
    was: "Berichte der Lokalzeitungen",
    schritte: [
      ["skript", "findet Wendungen wie „gegen die Stimmen von“ und legt den Belegsatz dazu"],
      ["ki", "ordnet den Artikel Sitzung, Tagesordnungspunkt und Dossier zu"],
      ["mensch", "prüft jeden Vorschlag am Artikel"],
    ] },
  { k: "notizen", titel: "Eigene Notizen", amtlich: false,
    was: "von Ratsmitgliedern, als Antwort auf die Liste ihrer offenen Stimmen",
    schritte: [
      ["skript", "erstellt je Person die Liste der offenen Abstimmungen"],
      ["skript", "liest die Antwort und trägt sie gekennzeichnet ein"],
    ] },
];

function prozessbild(b) {
  const zahlen = {
    niederschrift: `${b.vollstaendig} von ${b.sitzungen} Sitzungen`,
    auszug: `${b.auszug} Sitzungen`,
    presse: `${b.presse} Artikel`,
  };
  const punkte = liste => liste.map(([art, text]) =>
    html`<li class="m-mark ${art}">${text}</li>`);

  return html`
    <div class="m-legende" role="group" aria-label="Schritte hervorheben">
      <span>Hervorheben:</span>
      ${[["ki", "Sprachmodell"], ["skript", "Skript mit festen Regeln"],
         ["mensch", "Mensch entscheidet"]].map(([art, label]) =>
        html`<button type="button" class="m-mark ${art}" data-hl="${art}" aria-pressed="false">${label}</button>`)}
    </div>

    <div class="m-fluss">
      <div class="m-kopf m-k1">Quelle</div>
      <div class="m-kopf m-k2">Einarbeiten</div>

      ${QUELLEN.map(q => html`
        <button type="button" class="m-knoten m-quelle" data-k="${q.k}">
          <span class="m-herkunft">
            <strong>${q.titel}${q.amtlich && roh(' <span class="m-amtlich">amtlich</span>')}</strong>
            ${q.was}
            ${zahlen[q.k] && html`<span class="m-zahl">${zahlen[q.k]}</span>`}
          </span>
          <ul>${punkte(q.schritte)}</ul>
        </button>`)}

      <div class="m-schiene" aria-hidden="true"><i></i></div>

      <button type="button" class="m-knoten m-sammel" data-k="ableiten"
              data-vorspann="Alle Wege laufen hier zusammen">
        <strong>Rechenregeln und Prüfung</strong>
        <ul>${punkte([
          ["skript", "überträgt einstimmige Ergebnisse auf die Anwesenden"],
          ["skript", "errechnet die Gegenseite, wenn eine Seite vollständig bekannt ist"],
          ["skript", "ordnet am Tag eines Mandatswechsels den Sitz zu"],
          ["skript", "wertet aus, wer später kam oder früher ging"],
          ["skript", "prüft Form und Zusammenhang aller Dateien"],
          ["mensch", "gibt die Änderung frei"],
        ])}</ul>
      </button>

      <div class="m-pfeil" aria-hidden="true"><i></i></div>

      <button type="button" class="m-knoten m-bestand" data-k="bestand"
              data-vorspann="Daraus entsteht">
        <strong>Öffentliche Dateien</strong>
        <ul>${punkte([
          ["skript", "neun Dateien, jede Änderung mit Datum einsehbar"],
          ["skript", "der Browser rechnet die Anzeige selbst aus"],
        ])}</ul>
        <span class="m-zahl">Beim Besuch läuft kein Sprachmodell.</span>
      </button>
    </div>

    <div class="m-erklaerung" aria-live="polite"></div>`;
}

// -- Die Seite --

function renderMethodik(abschnitt) {
  const b = bestand();
  const t = tierCounts(sessionRegister().flatMap(votenVon));
  const nachvollziehbar = b.abstimmungen - t.sum;
  const seit = monatJahr(b.seit);

  const wrap = document.createElement("div");
  wrap.className = "methodik";
  wrap.innerHTML = html`
    <div class="topic-header">
      <h1>So entsteht diese Seite</h1>
      <div class="topic-summary">Was hier über Abstimmungen steht, stammt aus amtlichen
        Unterlagen der Stadt Moosburg oder ist anders gekennzeichnet. Diese Seite zeigt
        den Weg von der Quelle bis zur Anzeige: wo ein Sprachmodell mitarbeitet und wo feste
        Rechenregeln, und wie aus einem Ergebnis wie 20:3 wird, wer wie gestimmt hat.</div>
      <ul class="m-inhalt">
        ${[["weg", "Der Weg der Daten"], ["sprachmodell", "Sprachmodell"],
           ["herkunft", "Herkunft der Einzelstimmen"], ["go", "Regeln der Gemeindeordnung"],
           ["hausregeln", "Hausregeln"], ["betreiber", "Wer dahintersteht"],
           ["technik", "Technik"]].map(([id, label]) =>
          html`<li><a href="#/methodik/${id}" data-ziel="${id}">${label}</a></li>`)}
      </ul>
    </div>

    <section id="weg" class="m-abschnitt m-breit">
      <h2>Der Weg der Daten</h2>
      <p>Fünf Quellen speisen den Bestand, jede auf ihrem eigenen Weg. Danach laufen alle
        durch dieselben Rechenregeln. Ein Klick auf eine Karte erklärt sie.</p>
      ${prozessbild(b)}
    </section>

    <section id="sprachmodell" class="m-abschnitt">
      <h2>Wo ein Sprachmodell mitarbeitet</h2>
      <p>Seit ${seit} hat die Stadt ${b.vollstaendig} Niederschriften veröffentlicht,
        mit zusammen ${zahl(ausStufe("vollständig"))} Abstimmungen. Die ehrenamtlich
        von Hand abzutippen, wäre nicht zu leisten. Deshalb liest ein Sprachmodell die
        PDFs und überträgt sie in die Datenstruktur dieser Seite.
        Welches Modell, spielt kaum eine Rolle — entscheidend ist, was danach geprüft
        wird.</p>

      <div class="m-kasten m-zwei">
        <div class="m-tut">
          <h3>Das Sprachmodell übernimmt</h3>
          <ul>
            <li>Niederschriften lesen und in Tagesordnung, Beschlüsse, Stimmenzahlen und Anwesenheit übertragen</li>
            <li>vorschlagen, zu welchem Dossier ein Beschluss oder Artikel gehört</li>
            <li>Presseartikel der passenden Sitzung zuordnen</li>
            <li>Kurztexte zu Dossiers und Einträge der Zeitleisten entwerfen</li>
          </ul>
        </div>
        <div class="m-tut-nicht">
          <h3>Das Sprachmodell übernimmt nicht</h3>
          <ul>
            <li>Einzelstimmen erschließen — das tun nur die Rechenregeln unten</li>
            <li>Lücken füllen oder Ergebnisse schätzen</li>
            <li>Beschlüsse oder Personen bewerten</li>
            <li>etwas veröffentlichen, das kein Mensch durchgesehen hat</li>
          </ul>
        </div>
      </div>

      <p>Beim Übertragen entstehen Fehler. Deshalb prüfen Skripte nach jeder Änderung, ob
        die Zahlen aufgehen: Ja, Nein und Abwesende müssen die Zahl der Sitze ergeben,
        und jede Stimme muss zu einem Mitglied mit Mandat an diesem Tag gehören.</p>
      <p>Dieselbe Arbeitsteilung gilt überall: erster Aufschlag vom Sprachmodell,
        Korrektur und Freigabe durch einen Menschen. Die Niederschrift bleibt bei jeder
        Sitzung verlinkt; verbindlich ist sie.</p>
    </section>

    <section id="herkunft" class="m-abschnitt">
      <h2>Woher die Einzelstimmen stammen</h2>
      <p>Die Niederschrift nennt meist nur das Ergebnis, etwa 20:3. Wie sicher sich
        daraus Einzelstimmen ergeben, ist sehr verschieden; deshalb trägt jede
        Abstimmung eine Herkunftsangabe. So verteilen sich die
        ${zahl(b.abstimmungen)} erfassten
        Abstimmungen:</p>

      <div class="m-balken" role="img"
           aria-label="Verteilung der Herkunftsangaben über ${zahl(b.abstimmungen)} Abstimmungen">
        ${STUFEN.map(s => html`<span class="tier-${s.key}" data-n="${t[s.key]}"></span>`)}
      </div>
      <p class="m-skala"><span>0</span><span>Stimmverhalten nachvollziehbar bei
        ${zahl(nachvollziehbar)} von ${zahl(b.abstimmungen)}
        (${prozent(nachvollziehbar, b.abstimmungen)} %)</span><span>${zahl(b.abstimmungen)}</span></p>

      <ol class="m-stufen">
        ${STUFEN.map(s => html`
          <li>
            <span class="m-farbe tier-${s.key}"></span>
            <a href="#/datenlage/${s.key}">${s.titel}</a>
            <span class="m-n">${zahl(t[s.key])}<small>${prozent(t[s.key], b.abstimmungen)} %</small></span>
            <span class="m-was">${s.was}</span>
          </li>`)}
      </ol>

      <h3 class="m-unter">Drei Rechenregeln</h3>
      <p>Wo aus einem Ergebnis Einzelstimmen werden, geschieht das nach festen Regeln,
        für alle gleich und im Quellcode nachlesbar. Die drei Beispiele sind erfunden.</p>

      <div class="m-beispiele">
        <div class="m-beispiel">
          <h3>Einstimmig, alle haben mitgestimmt</h3>
          <div class="m-sitze" role="img" aria-label="22 Ja-Stimmen">
            ${Array.from({ length: 22 }, () => roh("<span></span>"))}
          </div>
          <p>22 anwesend, Ergebnis <b class="m-ergebnis">22:0</b>. Dann haben alle 22 mit
            Ja gestimmt.</p>
        </div>

        <div class="m-beispiel">
          <h3>Einstimmig, aber eine Stimme fehlt</h3>
          <div class="m-sitze" role="img" aria-label="22 abgeleitete Ja-Stimmen">
            ${Array.from({ length: 22 }, () => roh('<span class="stern"></span>'))}
          </div>
          <p>22 anwesend, Ergebnis <b class="m-ergebnis">21:0</b>. Eine Stimme fehlt,
            vielleicht war jemand kurz draußen; wer, steht nirgends. Die Seite leitet
            trotzdem für alle 22 ein Ja ab und markiert es mit einem Sternchen — solange
            mindestens 90 % der Stimmberechtigten mitgestimmt haben. Hier sind es 21 von
            22.</p>
          <p>Sonst gingen 21 richtige Angaben verloren, um eine falsche zu vermeiden.
            Unter 90 % bleibt es beim Fragezeichen. Zwei bekannte Ursachen rechnet die
            Seite vorher heraus, den Mandatswechsel und die Entlastung eines
            Aufsichtsrats. Und wo die Niederschrift vermerkt, wer später kam oder früher
            ging, bleibt nur dessen Stimme offen.</p>
        </div>

        <div class="m-beispiel">
          <h3>Eine Seite ist vollständig bekannt</h3>
          <div class="m-sitze" role="img"
               aria-label="7 bekannte Nein-Stimmen, 15 errechnete Ja-Stimmen">
            ${Array.from({ length: 7 }, () => roh('<span class="nein"></span>'))}
            ${Array.from({ length: 15 }, () => roh('<span class="gerechnet"></span>'))}
          </div>
          <p class="m-mini"><span><i class="nein"></i>aus der Presse</span><span><i class="gerechnet"></i>errechnet</span></p>
          <p>22 anwesend, Ergebnis <b class="m-ergebnis">15:7</b>. Ein Zeitungsbericht
            nennt alle sieben Gegenstimmen, also haben die übrigen 15 mit Ja gestimmt.
            Eine Subtraktion, in beide Richtungen. Die errechneten Stimmen tragen die
            Herkunft der Quelle, aus der sie folgen.</p>
        </div>
      </div>

      <p>Geht eine Stimme nur mittelbar aus der Quelle hervor, etwa aus einer zitierten
        Wortmeldung, ist sie als weicher Beleg gekennzeichnet.</p>

      <p>Wer einen Antrag gestellt hat, wird bei der Abstimmung über diesen Antrag mit Ja
        geführt, auch wenn die Niederschrift nur das Ergebnis nennt. Dass jemand gegen den
        eigenen Antrag stimmt, kommt praktisch nicht vor; die Stimme gilt deshalb als
        belegt und trägt den Vermerk „Antragsteller“.</p>

      <p>Manchmal geht die Zählung nicht auf, ohne dass die Niederschrift einen Grund
        nennt. Fehlt dieselbe eine Stimme bei allen Beschlüssen eines Abends, geht die
        Seite von einem Zählfehler aus und führt alle Anwesenden; der Beschluss trägt
        dann einen Hinweis. Fehlt sie nur bei einzelnen Beschlüssen, gilt die
        90-%-Regel von oben.</p>
    </section>

    <section id="go" class="m-abschnitt">
      <h2>Regeln der Gemeindeordnung</h2>
      <p>Einige Eigenheiten der Daten kommen aus der Bayerischen Gemeindeordnung (GO).</p>

      <div class="m-regeln">
        <div class="m-regel">
          <div><h3>Enthaltung gibt es nicht</h3><span class="m-paragraf">Art. 48 Abs. 1 Satz 2 GO</span></div>
          <div>
            <p>„Kein Mitglied darf sich der Stimme enthalten“, sagt die Gemeindeordnung.
              Wer da ist, stimmt mit Ja oder Nein. Zwei Ausnahmen gibt es:</p>
            <ul>
              <li><b>Niederschriften aus der Zeit vor dem eigenen Mandat.</b> Der Rat
                genehmigt die Niederschriften früherer Sitzungen. Wer damals nicht dabei
                war, kann sie nicht bestätigen und enthält sich.
                <a href="#/session/sr_20260518">Am 18. Mai 2026</a> betraf das elf neu
                gewählte Mitglieder: neun enthielten sich, zwei stimmten zu — welche
                zwei, hält die Niederschrift nicht fest. Die Seite führt deshalb alle elf
                als nicht stimmberechtigt und nennt die Aufteilung dazu.</li>
              <li><b>Persönliche Beteiligung</b>, dazu die nächste Regel.</li>
            </ul>
          </div>
        </div>

        <div class="m-regel">
          <div><h3>Persönliche Beteiligung</h3><span class="m-paragraf">Art. 49 GO</span></div>
          <div>
            <p>Wer an einer Entscheidung persönlich beteiligt ist, darf weder mitberaten
              noch mitstimmen: anwesend, aber ohne Stimme. Auf der Seite steht dafür das
              Zeichen §. In Moosburg etwa:</p>
            <ul>
              <li>die Entlastung des Aufsichtsrats der Kläranlage Moosburg GmbH, über die
                dessen Mitglieder aus dem Rat nicht mitstimmen</li>
              <li>Bauvorhaben, an denen ein Ratsmitglied selbst beteiligt ist</li>
              <li>Beschlüsse über das eigene Amt, etwa eine Aufwandsentschädigung</li>
            </ul>
            <p>In den erfassten Daten kommt das bei ${mitGrund("beteiligung")} von
              ${zahl(b.abstimmungen)} Abstimmungen vor.</p>
          </div>
        </div>

        <div class="m-regel">
          <div><h3>Wer mitstimmt</h3></div>
          <div><p>Im Stadtrat stimmen ${sitze("plenum") - 1} gewählte Mitglieder und der
            Erste Bürgermeister, zusammen ${sitze("plenum")} Stimmen. Die Ausschüsse sind
            kleiner, der Bau-, Planungs- und Umweltausschuss hat ${sitze("bpu")} Sitze.</p></div>
        </div>

        <div class="m-regel">
          <div><h3>Mandatswechsel</h3></div>
          <div><p>Scheidet jemand während der Wahlperiode aus, teilen sich ausscheidende und
            nachrückende Person an diesem Tag einen Sitz. Die ausscheidende stimmt bis
            zum Beschluss über den Wechsel; bei diesem Beschluss ist sie persönlich
            beteiligt und die Nachfolge noch nicht vereidigt, der Sitz stimmt also nicht
            mit. Danach gehört er der Nachfolge. Bisher betraf das
            ${sitzungenMitGrund("kein_mandat")} Sitzungen.</p></div>
        </div>

        <div class="m-regel">
          <div><h3>Kurz draußen ist nicht abwesend</h3></div>
          <div><p>Wer den Saal kurz verlässt, verpasst einzelne Abstimmungen, war aber da. Die
            Niederschrift vermerkt das als „ab 18:15 Uhr“ oder „bis 20:30 Uhr“; diese
            Vermerke werden ausgewertet. Ganz abwesend und für eine Abstimmung abwesend
            sind zweierlei.</p></div>
        </div>
      </div>
    </section>

    <section id="hausregeln" class="m-abschnitt">
      <h2>Hausregeln</h2>
      <p>Dazu kommen eigene Regeln. Sie sollen verhindern, dass hier mehr steht, als
        belegt ist.</p>
      <div class="m-regeln">
        <div class="m-regel">
          <div><h3>Nur Amtliches wird zum Bestand</h3></div>
          <div><ul>
            <li>Liegt nur ein Beschlussauszug vor, erscheinen die Ergebnisse.
              Stimmverhalten und Zuordnung zu einem Dossier warten auf die Niederschrift.</li>
            <li>Liegt nur eine Mitschrift vor, erscheint die Tagesordnung, aber kein
              Ergebnis.</li>
            <li>Für Sitzungen, die noch bevorstehen, gilt dasselbe.</li>
          </ul></div>
        </div>
        <div class="m-regel">
          <div><h3>Die Niederschrift hat Vorrang</h3></div>
          <div><p>Reihenfolge, Nummerierung und Titel der Tagesordnungspunkte kommen aus der
            Niederschrift. Weicht eine andere Quelle ab, wird das als Widerspruch
            vermerkt und nicht stillschweigend angeglichen.</p></div>
        </div>
        <div class="m-regel">
          <div><h3>Lücken bleiben sichtbar</h3></div>
          <div><p>Unbekanntes Stimmverhalten steht als Fragezeichen da. Sitzungen, zu
            denen nichts veröffentlicht ist, stehen trotzdem im Register, derzeit
            ${b.keine}. <a href="#/datenlage">Die Datenlage</a> zeigt zu jeder Sitzung,
            was vorliegt.</p></div>
        </div>
        <div class="m-regel">
          <div><h3>Beschreiben, nicht bewerten</h3></div>
          <div><p>Die Seite gibt wieder, was beschlossen wurde und wer wie abgestimmt hat. Die
            Texte zu Themen fassen Beschlusslage und Verlauf zusammen, ohne Meinung.
            Auch Kennzahlen wie die Abweichung von der eigenen Fraktion sind Zählungen,
            keine Urteile.</p></div>
        </div>
        <div class="m-regel">
          <div><h3>Nur der öffentliche Teil</h3></div>
          <div><p>Was der Rat nichtöffentlich berät, steht in keiner veröffentlichten
            Quelle und deshalb auch nicht hier.</p></div>
        </div>
      </div>
    </section>

    <section id="betreiber" class="m-abschnitt">
      <h2>Wer dahintersteht</h2>
      <div class="m-brief">
        <p>Die Seite wird privat von Benedict Gruber betrieben. Er saß von Oktober 2022
          bis April 2026 für fresh im Moosburger Stadtrat und war
          Digitalisierungsreferent der Stadt. Über viele der Beschlüsse, die hier
          stehen, hat er mit abgestimmt.</p>
        <p>Ziel ist eine sachliche Übersicht: was beschlossen wurde, wer wie abgestimmt
          hat, wie sicher das feststeht. Abgesichert ist das so:</p>
        <ul>
          <li>Dieselben Rechenregeln für alle, auch für die eigenen Abstimmungen. Sie
            stehen im Quellcode.</li>
          <li>Was aus eigenen Notizen stammt, ist gekennzeichnet, gleich von wem.</li>
          <li>Jede Änderung am Bestand ist mit Datum öffentlich nachvollziehbar.</li>
          <li>Fehler kann jede und jeder melden; Korrekturen sind genauso nachvollziehbar.</li>
        </ul>
        <p>Auf Dauer sollte die Seite nicht an einer Person hängen. Ratsmitglieder aller
          Fraktionen, Verwaltung, Lokalpresse, Vereine und Bürger:innen könnten sie
          gemeinsam tragen: Daten prüfen, Fehler melden, Notizen beisteuern,
          mitentscheiden, wie es weitergeht. Wer mitmachen will, meldet sich über das
          <button type="button" class="m-link" data-modal="kontakt-modal">Kontaktformular</button>.</p>
      </div>
    </section>

    <section id="technik" class="m-abschnitt">
      <h2>Technik</h2>
      ${[
        ["Kein Server, keine Datenbank",
         html`<p>Eine HTML-Datei, etwas JavaScript, neun JSON-Dateien. Ihr Browser lädt sie
           und rechnet den Rest selbst aus, etwa wer bei einer Abstimmung als abwesend
           gilt. Kein Framework, kein Server, der Daten verarbeitet. Dieselben Dateien
           laufen auf moosburg.eu und auf GitHub Pages.</p>`],
        ["Git als Gedächtnis",
         html`<p>Code und Daten liegen in einem öffentlichen Git-Repository, jede Änderung mit
           Datum und Begründung. Wann eine Stimme eingetragen oder korrigiert wurde und
           warum, steht in der
           <a href="https://github.com/bagruber/council/commits/main" target="_blank"
              rel="noopener">Änderungshistorie</a>.</p>`],
        ["Was gemessen wird",
         html`<p>Keine Cookies, keine fremden Dienste, nichts, was auf Ihrem Gerät abgelegt
           oder ausgelesen wird. Auch die Schriften liegen auf dem eigenen Server. Auf
           moosburg.eu zählt der Server die Aufrufe mit: Aufrufe derselben Sitzung fasst
           er über einen Hash aus IP, Browserkennung und einem täglich wechselnden
           Zufallswert zusammen, der sich nicht zurückrechnen lässt. Erst ein Klick auf
           einen Link zur Zeitung oder zur Stadt führt von hier weg.</p>`],
        ["Offene Daten",
         html`<p>Die Datendateien sind direkt abrufbar und mit JSON Schema beschrieben. Daten
           und Texte stehen unter CC BY-NC 4.0, der Code unter PolyForm Noncommercial
           1.0.0: weiterverwenden ja, kommerziell nein, Quelle nennen.</p>
           <p>Über die Lizenz hinaus dürfen Medien die Daten und Grafiken für
           redaktionelle Berichterstattung nutzen, auch wenn sie kommerziell arbeiten,
           sofern die Quelle genannt wird.</p>`],
        ["Wie Fehler abgefangen werden",
         html`<p>Nach jeder Änderung prüft ein Skript Form und Zusammenhang aller Dateien:
           jede Abstimmung gehört zu einer Sitzung, jede Stimme zu einem Mitglied mit
           Mandat an diesem Tag, die Zahlen gehen auf. Tests sichern die Rechenregeln
           ab.</p>`],
        ["Geplant: Daten direkt aus dem Ratsinformationssystem",
         html`<p>OParl ist eine offene Schnittstelle, über die Ratsinformationssysteme ihre
           Daten maschinenlesbar bereitstellen. Wo es sie gibt, soll sie das Auslesen
           der PDFs ersetzen.</p>`],
        ["Barrierefreiheit",
         html`<p>Unter „Über das Projekt“ lassen sich größere Schrift und farbenblind-sichere
           Farben einschalten. Die Grundschrift Atkinson Hyperlegible ist für
           eingeschränkte Sehkraft entworfen.</p>`],
      ].map(([titel, inhalt]) => html`
        <details class="m-details">
          <summary>${titel}</summary>
          <div>${inhalt}</div>
        </details>`)}
    </section>

    <div class="m-familie">
      <h2>Teil von moosburg.eu</h2>
      <p>Diese Seite gehört zu <a href="https://moosburg.eu/">moosburg.eu</a>, einer Sammlung
        ehrenamtlicher Projekte für Moosburg. Alle sind quelloffen, kostenlos und ohne
        Werbung.</p>
    </div>`;

  main.appendChild(backLink("Übersicht", "#/"));
  main.appendChild(wrap);

  // Die Balkenbreiten stehen erst hier fest; als Attribut im Markup waeren sie
  // ein Stilwert aus den Daten.
  wrap.querySelectorAll(".m-balken span").forEach(el => {
    el.style.flexGrow = el.dataset.n;
  });

  verdrahteProzessbild(wrap);
  verdrahteSprungziele(wrap);
  if (abschnitt) springe(wrap, abschnitt);
}

function springe(wrap, id) {
  const ziel = wrap.querySelector("#" + CSS.escape(id));
  if (ziel) ziel.scrollIntoView({ block: "start" });
}

// Die Sprungmarken aendern die Adresse, ohne die Seite neu zu bauen —
// sonst gingen aufgeklappte Abschnitte und der gewaehlte Kasten verloren.
function verdrahteSprungziele(wrap) {
  wrap.querySelectorAll("[data-ziel]").forEach(a => {
    a.addEventListener("click", e => {
      e.preventDefault();
      springe(wrap, a.dataset.ziel);
      history.replaceState(null, "", "#/methodik/" + a.dataset.ziel);
    });
  });
}

function verdrahteProzessbild(wrap) {
  const fluss = wrap.querySelector(".m-fluss");
  const kasten = wrap.querySelector(".m-erklaerung");

  const zeige = k => {
    fluss.querySelectorAll(".m-knoten").forEach(el =>
      el.classList.toggle("on", el.dataset.k === k));
    const e = ERKLAERUNG[k];
    kasten.innerHTML = html`
      <h3>${e.titel}</h3>
      ${e.absaetze.map(a => html`<p>${a}</p>`)}
      <p class="m-hinweis">Eine andere Karte anklicken für deren Erklärung.</p>`;
  };

  fluss.addEventListener("click", e => {
    const k = e.target.closest(".m-knoten");
    if (k) zeige(k.dataset.k);
  });

  const knoepfe = wrap.querySelectorAll(".m-legende button");
  knoepfe.forEach(b => b.addEventListener("click", () => {
    const an = b.getAttribute("aria-pressed") !== "true";
    knoepfe.forEach(x => x.setAttribute("aria-pressed", "false"));
    b.setAttribute("aria-pressed", String(an));
    if (an) fluss.dataset.hl = b.dataset.hl;
    else delete fluss.dataset.hl;
  }));

  schiene();
  document.fonts.ready.then(schiene);
  zeige("niederschrift");
}

// Die Schiene reicht genau vom ersten bis zum letzten Anschluss. Ihre Laenge
// haengt an den gerenderten Kaesten, steht also erst nach dem Satz fest — und
// aendert sich mit der Breite. Der Zuhoerer haengt am Fenster, nicht am
// Durchgang, sonst saesse nach jedem Rendern einer mehr daran.
function schiene() {
  const fluss = document.querySelector(".m-fluss");
  const s = fluss && fluss.querySelector(".m-schiene");
  const karten = fluss ? fluss.querySelectorAll(".m-quelle") : [];
  if (!s || !karten.length) return;
  const box = s.getBoundingClientRect();
  if (!box.height) return;
  const mitte = el => {
    const r = el.getBoundingClientRect();
    return r.top + r.height / 2;
  };
  s.style.setProperty("--oben", (mitte(karten[0]) - box.top - 1) + "px");
  s.style.setProperty("--unten", (box.bottom - mitte(karten[karten.length - 1]) - 1) + "px");
}

window.addEventListener("resize", schiene);

export { renderMethodik };
