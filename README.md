# Image2Commons
Deze repo bevat Python scripts voor het uploaden van de Beeldbank van Het Utrechts Archief naar Wikimedia Commons.
De code is generiek opgezet en hierdoor hopelijk ook geschikt voor andere archieven of GLAM-instellingen.

# Werkwijze
1. Maak een tabel (CSV bestand) met relevante metadata van de te uploaden afbeeldingen.
2. Download of kopieer de afbeeldingen die je wilt uploaden naar je computer.
3. Maak een template voor Wikimedia Commons (zie `templates/` map. Binnen het template kun je gebruik maken van Mediawiki en Liquid syntax.
4. Login op Commons met het volgende commando `./login2commons You@YourBot BotPassword`. Er wordt een Session Cookie bewaard in de huidige map
5. Voer het `./img2commons` script uit. Het script heeft vier parameters:
  CSV_FILE - de tabel met metadata van afbeeldingen die je wilt uploaden
  META_TEMPLATE_FILE - template voor de metadata per afbeelding
  LOCAL_IMAGE_TEMPLATE - mini template voor de bestandsnaam op je computer
  REMOTE_IMAGE_TEMPLATE - mini template hoe het bestand remote moet gaan heten. Gebruik een leesbare en duidelijke beschrijvende naam.

# Licentie
Dit script is vrij beschikbaar via de CC0 1.0 Publiek Domein Verklaring.
Bij vragen of opmerkingen mag je me mailen r.companje@hetutrechtsarchief.nl
