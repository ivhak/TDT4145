---
title: "Innlevering 1: Konseptuell datamodell"
author: [Iver Håkonsen, Kristian Hardang, Isak Collett, Nicolai Brummenæs]
date: "27.02.19"
lang: "nb"
header-includes: |
    \usepackage{dashundergaps}
...


## ER-diagram
![ER-diagram](img/ER2.png)

## Relasjonsdatabasemodell
* **Treningsøkt**( \underline{TreningsøktID} , Dato, Varighet, Prestasjon, Form)
* **Øvelse**( \underline{ØvelseID} , Navn)
* **Apparat**(\underline{ApparatID} , Navn, Beskrivelse) 
* **ØvelseApparat**( \underline{ØvelseID}, \dashuline{ApparatID}, AntallKilo, AntallSett)
    * ØvelseID fremmednøkkel til Øvelse, ApparatID fremmednøkkel til Apparat.
* **ØveleseFri**(\underline{ØvelseID}, Beskrivelse)
    * ØvelseID fremmednøkkel til Øvelse.
* **ØvelseIØkt**( \underline{TreningsøktID, ØvelseID})
    * TreningsøktID fremmednøkkel til Treningsøkt, ØvelseID fremmednøkkel til Øvelse.
* **Notat**( \underline{TreningsøktID} , Treningsformål, Refleksjon)
    * TreningsøktID fremmednøkkel til Treningsøkt.
* **ØvelsesGruppe**(\underline{GruppeID}, Navn}
* **ØvelseIGruppe**(\underline{GruppeID, ØvelseID})
    * GruppeID fremmednøkkel til ØvelsesGruppe, ØvelseID fremmednøkkel til Øvelse.

## Beskrivelse av krav 
1. Registrere apparater, øvelser og treningsøkter med tilhørende data:
    * Et apparat kan registres i `Apparat` uavhengig av alt annet, siden det ikke er en
      svak klasse.  Dersom øvelsen bruker fast apparat, kan denne refereres til,
      og en øvelse kan dermed opprettes. En treningsøkt kan også opprettes
      uavhengig. Når både øvelsen og treningsøkten er opprettet, kan id'ene
      settes inn i `ØvelseIØkt`.

2. Få opp informasjon om et antall _n_ sist gjennomførte treningsøkter med
   notater, der n spesifiseres av brukeren:
    * Siden treningsøktene har en dato, kan man kombinere `Treningsøkt` med
      `Notat`, sortere på dato og velge de n første. 
      
3. For hver enkelt øvelse skal det være mulig å se en resultatlogg i et gitt
   tidsintervall spesifisert av brukeren:
    * Kan kombinere `Treningsøkt` og `Øvelse` og hente enten `AntallKilo` og
      `AntallSett` dersom øvelsen er på apparat eller `Beskrivelse` dersom
      øvelsen er fri. I `Treningsøkt` er datoen for økten lagret, så det er
      mulig kun hente fra det gitte tidsintervallet.

4. Lage øvelsesgrupper og finne øvelser som er i samme gruppe:
    * Siden `ØvelsesGruppe` er en egen tabell uten noen fremmednøkler, kan en
      gruppe initialiseres  uten at noen øvelser er i den enda. Dersom en
      øvelse og en gruppe begge er opprettet, kan  de legges i `ØvelseIGruppe`.
      Øvelse som er i samme gruppe kan da finnes ved å joine `Øvelse`,
      `ØvelseIGruppe` og `ØvelsesGruppe` og gruppere etter gruppenavn.

5. Et valgfritt use case som dere selv bestemmer:
    * Vårt valgfrie use case er at brukeren skal ha mulighet til å få en
      oversikt  over hvilke apprater den bruker mest, og hvor mange ganger hver
      er brukt.  Dette kan utføres ved å kombinere `Apparat` og
      `ØvelseFastApparat`, gruppere etter navn på apparatet og telle antall
      forekomster.
