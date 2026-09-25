# Cartesia Sonic-3.6

Reference for the **Cartesia Sonic-3.6** tab. Snapshot taken on 2026-09-25 from
the Cartesia API (`GET /voices`, public voices) and Cartesia's pricing pages;
prices and the voice catalog change, so confirm at <https://cartesia.ai/pricing>
and <https://play.cartesia.ai>.

## 1. API or local?

**API only.** Sonic-3.6 (`model_id: sonic-3.6`) is hosted by Cartesia; there
are no downloadable weights. Local, on-prem, VPC or on-device deployment exists
only through an enterprise contract (Sonic On-Device is in private beta).
Text is sent to Cartesia's servers, so it needs an API key and network access.

## 2. Pricing

Text-to-speech is billed in **credits, about 1 credit per character** of
input text (not per second of audio). Credits expire at the end of each
billing cycle.

| Plan | Price / month | Credits / month | Concurrent TTS | Notable |
| --- | --- | --- | --- | --- |
| Free | $0 | 20K | 2 | No commercial use, no voice cloning (per third-party summaries) |
| Pro | $5 | 100K | 3 | Commercial license, instant voice cloning |
| Startup | $49 | 1.25M | 5 | Professional voice cloning, organization support |
| Scale | $299 | 8M | 15 | Priority support, higher concurrency |
| Enterprise | Custom | Custom | Custom | Volume pricing, DPA/BAA, SSO, on-prem/on-device |

Approximate cost per 1M characters, computed from the table (price / credits,
at 1 credit per character, assuming the plan is fully used): Pro about $50,
Startup about $39, Scale about $37. Unused credits are lost, so real cost is
higher when usage is below the plan's quota. Overage rates are not published
on the pages we could read; check the pricing FAQ.

Other items: voice agents cost $0.06/min (+ $0.014/min telephony); speech to
text (Ink) is billed per second (`ink-2`: 3 credits/s); Pro Voice Cloning is
reported at 1.5 credits per character plus a one-time training fee.

Rule of thumb for this playground: the sample text is about 100 characters,
so the free tier covers roughly 200 generations per month.

## 3. Accents (`locale`)

The **Accent (locale)** selector sends the API's `locale`. Accepted in our
tests: `es-MX`, `es-ES`, `es-US`, `pt-BR`, `pt-PT`, `en-US`, `en-GB`, `en-AU`,
`en-IN`, `en-CA`, `en-ZA`. Rejected with HTTP 400: `es-AR`, `es-CO`, `es-PE`.
Each voice has a native accent (column *Native locale* below); other locales
are approximations, so judge them by ear.

Native accents in the catalog (voice counts): Spanish es-MX 42, es-ES 38,
es-CO 4, es-BO 2; Portuguese pt-BR 15, pt-PT 8; English en-US 312, en-GB 45,
en-AU 31, en-ZA 11, en-IN 8, en-NZ 6, en-SG 5, en-IE 3, en-CA 2. So a
Colombian accent is available by **choosing an es-CO voice** (e.g. Catalina),
even though the `es-CO` locale value is rejected by the API; there are no
Argentine or Peruvian native voices. Pass the voice id via *Custom* in the tab.

## 4. Available voices

Public voices in the library: **87 Spanish, 23 Portuguese, 427 English**. Gender is the library's `gender` field (F feminine, M masculine, N neutral). The voices in the tab's *Voice preset* dropdown are a small recommended subset.

### Spanish (87: 49 F, 38 M)

| Name | Gender | Native locale | Accent | Tagline | Voice ID |
| --- | --- | --- | --- | --- | --- |
| Gerard | M | - | - | Thoughtful Explainer | `c4680a72-a9d5-4c16-8858-6f6caf761e7b` |
| Carmen | F | es-BO | camba | Friendly Neighbor | `727f663b-0e90-4031-90f2-558b7334425b` |
| Javier | M | es-BO | camba | Gentle Advisor | `e9f0368b-3662-4a01-b037-e13ca5203c74` |
| Catalina | F | es-CO | colombian | Neighborly Guide | `162e0f37-8504-474c-bb33-c606c01890dc` |
| Cedric | M | es-CO | colombian | Coach Desk | `5539dace-8bf7-44c1-a603-160e69e740ca` |
| Jeronimo | M | es-CO | colombian | Empathetic Advisor | `7c1ecd2d-1c83-4d5d-a25c-b3820a274a2e` |
| Mariana | F | es-CO | colombian | Nurturing Guide | `ae823354-f9be-4aef-8543-f569644136b4` |
| Ainsley | F | es-ES | castilian | Training Host | `d6032980-a170-4fdc-adfc-aabc93db0ae4` |
| Alicia | F | es-ES | castilian | Walkthrough Guide | `5522c839-bbd9-4485-8d84-ba3d75cd3330` |
| Alondra | F | es-ES | castilian | Reassuring Sister | `ccfea4bf-b3f4-421e-87ed-dd05dae01431` |
| Benito | M | es-ES | castilian | Digital Voice | `02aeee94-c02b-456e-be7a-659672acf82d` |
| Blanca | F | es-ES | castilian | Graceful Host | `538a8872-3799-4df5-b373-b78493b766c6` |
| Camila | F | es-ES | castilian | Happy Conversationalist | `bef2ba57-5c10-433b-b215-3bef35110a81` |
| Camila | F | es-ES | castilian | - | `30212483-5c20-479c-8121-f93cd24e30a6` |
| Carlos | M | es-ES | castilian | - | `9ebc775b-c579-4c31-b37c-2306cbe9cc91` |
| Celia | F | es-ES | castilian | Practical Analyst | `ad38904c-0ce9-42b1-9159-5ad5352ef089` |
| Darío | M | es-ES | castilian | Steady Operator | `35b2cfc1-e6fb-4d69-a598-c1780612be4a` |
| Diego | M | es-ES | castilian | Hype Guy | `399002e9-7f7d-42d4-a6a8-9b91bd809b9d` |
| Elena | F | es-ES | castilian | Narrator | `cefcb124-080b-4655-b31f-932f3ee743de` |
| Eva | F | es-ES | castilian | Service Expert | `23da166b-9675-425a-a56f-10d92da2e35f` |
| Flor | F | es-ES | castilian | Hold Companion | `b8f073cd-cb60-43ef-aa01-feb59a8b7394` |
| Gonzalo | M | es-ES | castilian | Grounded Storyteller | `58e531e3-b212-49df-adee-c335a19c2429` |
| Hector | M | es-ES | castilian | Tour Leader | `b042270c-d46f-4d4f-8fb0-7dd7c5fe5615` |
| Ines | F | es-ES | castilian | Route Guide | `db74bd0c-9ea6-4d08-b78e-c3c0a54dfd2d` |
| Iria | F | es-ES | castilian | Thoughtful Communicator | `a7beff01-8f8b-4809-bfe6-e2166e57e0c2` |
| Isabel | F | es-ES | castilian | Teacher | `c0c374aa-09be-42d9-9828-4d2d7df86962` |
| Julia | F | es-ES | castilian | Loyalty Host | `e52c4915-8320-4215-9c1f-81bad7ca0d5d` |
| Lara | F | es-ES | castilian | Customer Liaison | `85b356c1-c638-404d-b986-f54a53d957d6` |
| Liliana | F | es-ES | castilian | Doting Mother | `b503f001-80b8-49d3-8666-8d7700fc5ca2` |
| Lucia | F | es-ES | castilian | Radiant Host | `c0925108-d541-4dc4-bbae-39f4e57ba10c` |
| Luis | M | es-ES | castilian | News Caster | `b5aa8098-49ef-475d-89b0-c9262ecf33fd` |
| Maite | F | es-ES | castilian | Bridge Desk | `b738fa95-b787-4529-9170-34be41e95b95` |
| Manuel | M | es-ES | castilian | Newsman | `948196a7-fe02-417b-9b6d-c45ee0803565` |
| Marcos | M | es-ES | castilian | Steady Advisor | `13ff5deb-2591-42ad-a356-63a04e524411` |
| Marta | F | es-ES | castilian | Friendly Guide | `de38f545-c574-44e8-9b54-a7d6fec1c6b1` |
| Miguel | M | es-ES | castilian | Route Guide | `d813d699-27f0-4231-83b4-6bd1bce106ba` |
| Noa | F | es-ES | castilian | Professional Assistant | `3408d527-179f-434a-94cb-962d5578642d` |
| Nuria | F | es-ES | castilian | Trusted Advisor | `9d8c6b2e-0a23-4a15-ae1b-121d5b5af417` |
| Octavio | M | es-ES | castilian | Service Anchor | `9aea78cb-ba89-4a82-aa15-31b55a89b75d` |
| Paloma | F | es-ES | castilian | Clear Presenter Woman | `d4db5fb9-f44b-4bd1-85fa-192e0f0d75f9` |
| Rafael | M | es-ES | castilian | Poised Advisor | `cbb6fdf0-30dd-49f6-af7d-bbb1185c1fa5` |
| Renata | F | es-ES | castilian | Cheerful Conversationalist | `d3793b7b-4996-409c-9d59-96dd09f47717` |
| Rosa | F | es-ES | castilian | Optimist Mother | `fb936dd1-66ea-43a0-86bd-18a6203dcda2` |
| Thiago | M | es-ES | castilian | Measured Professional | `21c2f7ab-dacb-4847-a593-3cd20668c4b3` |
| Álvaro | M | es-ES | castilian | Steady Explainer | `ca526927-b7c8-4a64-95d7-235d30b7771f` |
| Adriana | F | es-MX | mexican | Bright Entertainer | `f4d6bb07-f876-4464-ba70-cd48d8701890` |
| Agustin | M | es-MX | mexican | Clear Storyteller | `2695b6b5-5543-4be1-96d9-3967fb5e7fec` |
| Aitana | F | es-MX | mexican | Direct Assistant | `80256320-7688-4ad3-a062-39b37bbfab33` |
| Alejandro | M | es-MX | mexican | Calm Mentor | `3a35daa1-ba81-451c-9b21-59332e9db2f3` |
| Alonso | M | es-MX | mexican | Podcast Explainer | `4853bafa-52cc-48c8-86a1-1edf8c76e429` |
| Andres | M | es-MX | mexican | Trusted Voice | `d46e87a1-7c6d-4b18-9359-926f4a35ffdf` |
| Arturo | M | es-MX | mexican | Professional Assistant | `ed8a381a-0704-4d12-8544-0560cc3f32da` |
| Carolina | F | es-MX | mexican | Friendly Guide | `3797b3c0-ab71-40dc-bfa0-a8c6ff9c1e8b` |
| Cesar | M | es-MX | mexican | Friendly Server | `4b5112be-c461-44a2-a66b-0dd7f98db4a0` |
| Daniela | F | es-MX | mexican | Relaxed Woman | `5c5ad5e7-1020-476b-8b91-fdcbe9cc313c` |
| Danna | F | es-MX | mexican | Operational Guide | `5f62aab4-c423-4ef8-ab37-5e0d7a0c430e` |
| David | M | es-MX | mexican | System Architect | `f82acaf6-ee56-417f-8f7f-bcd72dad3022` |
| Eduardo | M | es-MX | mexican | Steady Communicator | `3efb11f3-4c0e-43c2-bad5-85ab99e993e2` |
| Emilio | M | es-MX | mexican | Friendly Optimist | `b0689631-eee7-4a6c-bb86-195f1d267c2e` |
| Esteban | M | es-MX | mexican | Crisp Operator | `392e340d-bf73-4199-9f46-8baca484f4cb` |
| Fernanda | F | es-MX | mexican | Friendly Guide | `b4b8e2af-6139-466e-a93a-30c20d2e1fc5` |
| Guadalupe | F | es-MX | mexican | Wise Storyteller | `dbaa1a0d-e004-442d-866f-5431b18d8d54` |
| Iker | M | es-MX | mexican | Thoughtful Advisor | `e4411d96-83e8-4e3a-b336-1d55a6f5eb31` |
| Jimena | F | es-MX | mexican | Calm Assistant | `cda9a0ca-0378-420a-9697-2241be5db771` |
| Jorge | M | es-MX | mexican | Regular Guy | `7b001dff-b8b2-4da7-92e4-5c794798effa` |
| Jose | M | es-MX | mexican | Patient Explainer | `3ca54c01-ef9a-4f44-9f73-adbde3a26ef8` |
| Juanita | F | es-MX | mexican | Helpful Companion | `c68a8bd0-f99e-4e7f-915d-a097da6d024c` |
| Kenia | F | es-MX | mexican | Efficient Explainer | `ffd984de-0b16-49f7-8a1a-13b2806a8ad0` |
| Laura | F | es-MX | mexican | Trustworthy Guide | `1cc00672-e9d4-455e-b3fb-31dfb7aad231` |
| Luciana | F | es-MX | mexican | Calm Desk | `d5225a22-5ecd-4564-ac87-ab77eb5d424f` |
| Mateo | M | es-MX | mexican | Friendly Host | `2fc4f1ec-bfd0-46f1-8e6d-d4279eaaf838` |
| Matias | M | es-MX | mexican | Status Desk | `60756a43-e015-4c84-927b-6a02ed32d0b4` |
| Natalia | F | es-MX | mexican | Resolution Expert | `4a25dee4-d62c-4418-8ad5-886103b940fa` |
| Nayeli | F | es-MX | mexican | Calculated Specialist | `d26313b0-ddd1-4daf-9cd1-d9b39c026a3a` |
| Pablo | M | es-MX | mexican | Reliable Contact | `61510db3-e266-4dfb-8dd6-e4f976b1351e` |
| Paola | F | es-MX | mexican | Expressive Performer | `e361b786-2768-4308-9369-a09793d4dd73` |
| Pedro | M | es-MX | mexican | Formal Speaker | `15d0c2e2-8d29-44c3-be23-d585d5f154a1` |
| Ramon | M | es-MX | mexican | Calm Coordinator | `9b67072c-d46c-465d-87dc-f7a1c6db2bf3` |
| Regina | F | es-MX | mexican | Friendly Specialist | `e5e5c8d7-3924-4ff6-981a-cb667034be29` |
| Rodrigo | M | es-MX | mexican | Calm Companion | `079e3a17-5545-4bc5-93e3-e11df6fe37b8` |
| Santiago | M | es-MX | mexican | Modern Navigator | `bef24f4f-adc9-4cef-acbf-cc1ceb98224b` |
| Sofía | F | es-MX | mexican | Digital Concierge | `4663e61a-a9c2-40e1-94c5-c461ed9d3d31` |
| Ursula | F | es-MX | mexican | Travel Desk | `c50d415d-a023-4cf2-817f-6b05c1be9d35` |
| Valeria | F | es-MX | mexican | Cheerful Promoter | `ad8eee76-d702-4a1f-a1bd-7596755ae4c9` |
| Veronica | F | es-MX | mexican | Warm Helper | `a0149de0-42cd-45b6-be89-5fb7baf6c6e7` |
| Ximena | F | es-MX | mexican | Calm Navigator | `3597a26f-80ef-4bd5-8101-9699bc764917` |
| Yadira | F | es-MX | mexican | Policy Explainer | `5ba248b0-29d8-4c62-a8af-366eaa17a310` |

### Portuguese (23: 12 F, 11 M)

| Name | Gender | Native locale | Accent | Tagline | Voice ID |
| --- | --- | --- | --- | --- | --- |
| Alice | F | pt-BR | brazilian-portuguese | Informative Speaker | `9904416a-0831-44ea-b8ee-5f145e8f9bbf` |
| Ana Paula | F | pt-BR | brazilian-portuguese | Marketer | `1cf751f6-8749-43ab-98bd-230dd633abdb` |
| Bruno | M | pt-BR | brazilian-portuguese | Reliable Communicator | `b603811e-54c2-4a0a-8854-09eab9ffa63f` |
| Eloá | F | pt-BR | brazilian-portuguese | Engaging Explainer | `cb2694c3-715f-4da9-99f3-1c974fff2928` |
| Fabiana | F | pt-BR | brazilian-portuguese | Clear Desk | `81452d3b-a5f6-4ef4-afff-542182fac725` |
| Felipe | M | pt-BR | brazilian-portuguese | Warm Assistant | `616c64d7-f541-436b-9b8d-e79cfbe19ef9` |
| Gustavo | M | pt-BR | brazilian-portuguese | Steady Advisor | `28a942b5-74f3-47bb-9b56-4c3f2562d3ba` |
| Heitor | M | pt-BR | brazilian-portuguese | Easygoing Local | `b0f46533-d4bb-493f-a26f-a99e1f2e86e3` |
| Helena | F | pt-BR | brazilian-portuguese | Solution Facilitator | `8a6d0b8e-8cd8-4952-a41e-b7af18662135` |
| Isabella | F | pt-BR | brazilian-portuguese | Warm Storyteller | `c9611be8-aae9-4a93-bb1c-98dd6b7d52a4` |
| Joao | M | pt-BR | brazilian-portuguese | Policy Desk | `c8750946-6b70-4dbf-b760-8cc554e98a0c` |
| Larissa | F | pt-BR | brazilian-portuguese | Bright Companion | `8d826d43-20ad-4c56-8d37-1048eccca1bf` |
| Luana | F | pt-BR | brazilian-portuguese | Public Speaker | `700d1ee3-a641-4018-ba6e-899dcadc9e2b` |
| Mirella | F | pt-BR | brazilian-portuguese | Upbeat Speaker | `2f4d204f-a5dc-4196-81bc-155986b76ab6` |
| Rafael | M | pt-BR | brazilian-portuguese | Dynamic Speaker | `07b6f895-78b9-4921-8e10-8a21c99c2e8a` |
| Beatriz | F | pt-PT | european-portuguese | Support Guide | `d4b44b9a-82bc-4b65-b456-763fce4c52f9` |
| Diogo | M | pt-PT | european-portuguese | Promotion Lead | `fbee0e7d-a83a-4082-bad1-13c70f86da4e` |
| Gaspar | M | pt-PT | european-portuguese | Considerate Listener | `e6b8bb73-2655-433d-8a10-7b8cf559d03b` |
| Isabel | F | pt-PT | european-portuguese | Confident Woman | `f39bf583-3b3d-402f-9ffb-6179d9ec3e35` |
| Mariana | F | pt-PT | european-portuguese | Welcome Host | `d9300964-8269-4ca8-9e8e-4ae714fcdc09` |
| Matias | M | pt-PT | european-portuguese | Process Explainer | `b1d18488-4aaa-47e7-9e4b-483c90a67968` |
| Paulo | M | pt-PT | european-portuguese | Transfer Desk | `250fdc17-cc1b-4ff1-8538-63988791cd3e` |
| Tiago | M | pt-PT | european-portuguese | Narration Expert | `6a360542-a117-4ed5-9e09-e8bf9b05eabb` |

### English (427: 213 F, 213 M, 1 N)

| Name | Gender | Native locale | Accent | Tagline | Voice ID |
| --- | --- | --- | --- | --- | --- |
| Daniela | F | - | - | Guidance Specialist | `c8ad77a8-42b9-4f69-8ed3-a2801c3e223d` |
| Gabriela | F | - | - | Account Guide | `741a0606-3f3a-430e-a928-aa81be7a5aef` |
| Ricardo | M | - | - | Calm Problem-Solver | `8499aae3-022c-4d55-8283-0c2e8adbefb4` |
| Aila | F | en-AU | australian | Paced Helper | `a0e8430e-1267-4a4d-baa5-a5d5e53122a9` |
| Amelia | F | en-AU | australian | Instructor | `043cfc81-d69f-4bee-ae1e-7862cb358650` |
| Arlo | M | en-AU | australian | Service Specialist | `12e85709-099c-480a-ba3e-875c41a9611a` |
| Barry | M | en-AU | australian | Helper | `13524ffb-a918-499a-ae97-c98c7c4408c4` |
| Barry 2.0 | M | en-AU | australian | Helper | `4fb26a05-57de-4d21-855a-f51adae44f38` |
| Blair | F | en-AU | australian | Triage Ally | `fd91495f-b8da-4944-ab8f-674c13089d7f` |
| Bronte | F | en-AU | australian | Trusted Guide | `391f4c0a-f1a8-4c21-9aa2-7a07f0a4b0dc` |
| Callum | M | en-AU | australian | Brand Spokesperson | `da4a4eff-3b7e-4846-8f70-f075ff61222c` |
| Cooper | M | en-AU | australian | Friendly Mate | `49743b08-0f5d-4741-839c-b12933853780` |
| Eleanor | F | en-AU | australian | Composed Clarifier | `7d7d769c-5ab1-4dd5-bb17-ec8d4b69d03d` |
| Ella | F | en-AU | australian | Caring Scout | `2a12b36c-7f9b-4c3a-9f7a-72731b15323a` |
| Ethan | M | en-AU | australian | Casual Assistant | `f0e50f2a-9116-4510-9c5b-fec928daff4b` |
| Fraser | M | en-AU | australian | Trusted Communicator | `79d2cf27-444a-4c3a-9eed-2ad5cf795a3b` |
| Grace | F | en-AU | australian | Helpful Hand | `c2ad7092-0447-47ea-948b-61fbb6faf153` |
| Haven | F | en-AU | australian | Survey Host | `f014dce5-df0e-4cfa-98e1-bd4bb73bb0b1` |
| Heath | M | en-AU | australian | Calm & Composed | `eb7d0d3b-e427-483b-bbca-1c009c33f8a7` |
| Jasper | M | en-AU | australian | Vibrant Stylist | `e98bd614-9b9d-4031-b930-ed72482af858` |
| Liam | M | en-AU | australian | Guy Next Door | `41f3c367-e0a8-4a85-89e0-c27bae9c9b6d` |
| Lori | F | en-AU | australian | Scared Cheerleader | `fb78f09f-f998-4061-ad51-d71f90388f0e` |
| Lori | F | en-AU | australian | Surprised Cheerleader | `c2da2a3e-b0d6-46bf-a09a-68562617a50a` |
| Lori | F | en-AU | australian | Curious Cheerleader | `ba0add52-783c-4ec0-8b9c-7a6b60f99d1c` |
| Lori | F | en-AU | australian | Happy Cheerleader | `8843adfb-77d3-455a-86f9-de0651555ec6` |
| Lori | F | en-AU | australian | Cheerleader | `5cc54223-ec0c-4c50-87e9-b9947264e1f4` |
| Lori | F | en-AU | australian | Disgusted Cheerleader | `414da90b-16b3-4e88-86f5-3c3945e8fa4b` |
| Lori | F | en-AU | australian | Sad Cheerleader | `2d01710c-7c77-4cf1-b0d0-5902a25f6e17` |
| Lori | F | en-AU | australian | Cheerleader | `57c63422-d911-4666-815b-0c332e4d7d6a` |
| Olivia | F | en-AU | australian | Sunny Woman | `f31cc6a7-c1e8-4764-980c-60a361443dd1` |
| Paul | M | en-AU | australian | Straight Talker | `3e1ed423-17e5-4773-b87c-25b031106e41` |
| Peyton | F | en-AU | australian | Peer Ally | `f4e419a9-fc75-4252-9d4e-93e4247f07c9` |
| Robyn | F | en-AU | australian | Storycrafter | `8985388c-1332-4ce7-8d55-789628aa3df4` |
| Suzanne | F | en-AU | australian | Laidback Aunt | `8634bd27-0acf-4056-b014-4fea0385ed9e` |
| Darla | F | en-CA | canadian-english | Resolution Agent | `996a8b96-4804-46f0-8e05-3fd4ef1a87cd` |
| Max | M | en-CA | canadian-english | Conversational Support | `3945925b-9143-4b7d-9ab5-cc4878001106` |
| Ailsa | F | en-GB | british | Warm Guide | `fb02b554-7d64-4f90-841e-e57fc88f410c` |
| Alaric | M | en-GB | british | Wizard | `87748186-23bb-4158-a1eb-332911b0b708` |
| Alec | M | en-GB | british | Spirited Salesman | `17044048-bfab-44b2-9532-9c1b65e9c217` |
| Alfie | M | en-GB | british | Composed Advisor | `5e7d492a-5502-482e-b315-ebf587427806` |
| Alistair | M | en-GB | british | Composed Consultant | `c8f7835e-28a3-4f0c-80d7-c1302ac62aae` |
| Archie | M | en-GB | british | Approachable Mate | `ef191366-f52f-447a-a398-ed8c0f2943a1` |
| Arthur | M | en-GB | british | Polished Advisor | `bb7e8daa-8b79-47a2-8408-a7a1cc72b53c` |
| Benedict | M | en-GB | british | Measured Mediator | `3c0f09d6-e0d7-499c-a594-70c5b7b93048` |
| Benedict | M | en-GB | british | Royal Narrator | `7cf0e2b1-8daf-4fe4-89ad-f6039398f359` |
| Casper | M | en-GB | british | Gentle Narrator | `4f7f1324-1853-48a6-b294-4e78e8036a83` |
| Caspian | M | en-GB | british | Oracle | `d7862948-75c3-4c7c-ae28-2959fe166f49` |
| Charlotte | F | en-GB | british | Heiress | `71a7ad14-091c-4e8e-a314-022ece01c121` |
| Clive | M | en-GB | british | Measured Expert | `b24f41fd-00a3-4cd8-992a-a0c9f13f3ef1` |
| Cora | F | en-GB | british | Service Specialist | `c46cf1f6-49a1-4d67-9a57-ff859a4046d3` |
| Courtney | F | en-GB | british | Composed Professional | `16a4052e-1f11-47ac-95f5-9330bee062f9` |
| Evelyn | F | en-GB | british | Digital Assistante | `3c7dfd17-3fa8-47aa-aacc-6313fe025442` |
| Evie | F | en-GB | british | Engaging Expert | `e5d4c33a-d8f6-46e8-a10f-b5afecc35648` |
| Finn | M | en-GB | british | Engaging Host | `15070120-82ab-48e5-87e5-c4bf28fa4bf9` |
| Fiona | F | en-GB | british | Witty Woman | `a01c369f-6d2d-4185-bc20-b32c225eab70` |
| Gary | M | en-GB | british | Composed Advisor | `dc52ada6-0e11-4684-a8fa-e0af5b7bdcb2` |
| Gemma | F | en-GB | british | Decisive Agent | `62ae83ad-4f6a-430b-af41-a9bede9286ca` |
| George | M | en-GB | british | Composed Consultant | `4bc3cb8c-adb9-4bb8-b5d5-cbbef950b991` |
| Griffin | M | en-GB | british | Narrator | `c99d36f3-5ffd-4253-803a-535c1bc9c306` |
| Griffin | M | en-GB | british | Excited Narrator | `34d923aa-c3b5-4f21-aac7-2c1f12730d4b` |
| Harrison | M | en-GB | british | Diligent Detailer | `df89f42f-f285-4613-adbf-14eedcec4c9e` |
| Hugo | M | en-GB | british | Teatime Friend | `1463a4e1-56a1-4b41-b257-728d56e93605` |
| Imogen | F | en-GB | british | Polished Guide | `5a93ae96-9e3e-4b9d-8575-5f62b7de6d0f` |
| Jasper | M | en-GB | british | Service Specialist | `3faa81ae-d3d8-4ab1-9e44-e50e46d33c30` |
| Julia | F | en-GB | british | Gentle Guide | `273f9ef7-9fc2-4def-88bb-ab108c6249ca` |
| Lucy | F | en-GB | british | Capable Coordinator | `2f251ac3-89a9-4a77-a452-704b474ccd01` |
| Martin | M | en-GB | british | Meticulous Operator | `dcddf1f4-b114-4b5d-9158-895cbba0e406` |
| Miles | M | en-GB | british | Yogi | `f114a467-c40a-4db8-964d-aaba89cd08fa` |
| Oliver | M | en-GB | british | Customer Chap | `ee7ea9f8-c0c1-498c-9279-764d6b56d189` |
| Oscar | M | en-GB | british | Clear Specialist | `22df7143-7987-4e15-a720-d65c69a443b3` |
| Owen | M | en-GB | british | Support Anchor | `0ea47942-be0b-4bc7-a1bf-5dba008dc1cc` |
| Pippa | F | en-GB | british | Bright Assistant | `81cd8d19-45e7-47b2-ad0e-bcd94f557ad0` |
| Quentin | M | en-GB | british | Refined Narrator | `5568a7df-e5ab-4442-9fae-2e9ba1b15ad8` |
| Rowan | M | en-GB | british | Steady Guide | `8c254787-4eb4-4577-bd3d-fb3c273baea2` |
| Roy | M | en-GB | british | Stern Realist | `f2ddbdca-59d9-4363-abeb-a197d65ea24a` |
| Rupert | M | en-GB | british | Caring Dad | `0ad65e7f-006c-47cf-bd31-52279d487913` |
| Saira | F | en-GB | british | Organized Coordinator | `1e9b9b3d-d2ce-4cac-9d05-bc36a63fa28e` |
| Spencer | M | en-GB | british | Chill Gentleman | `3bf35adc-bcc4-464b-b834-c90c88cf6492` |
| Toby | M | en-GB | british | Genuine Guide | `3d5ce2fb-e56c-42f0-9ed9-4662484063b4` |
| Trevor | M | en-GB | british | Movieman | `c45bc5ec-dc68-4feb-8829-6e6b2748095d` |
| Victoria | F | en-GB | british | Refined Coordinator | `dc30854e-e398-4579-9dc8-16f6cb2c19b9` |
| Conor | M | en-IE | irish | Decisive Agent | `1ec736fa-db96-4eea-9299-235ce2cb7a0e` |
| Ronan | M | en-IE | irish | Steady Advisor | `d3e3d5d5-07b0-484f-9967-dbc8f15b60d5` |
| Siobhan | F | en-IE | irish | Warm Welcomer | `d79d2b77-9192-4e10-9407-5d43ca034803` |
| Aarav | M | en-IN | indian-english | Old Time Storyteller | `39d518b7-fd0b-4676-9b8b-29d64ff31e12` |
| Devansh | M | en-IN | indian-english | Warm Support Agent | `1259b7e3-cb8a-43df-9446-30971a46b8b0` |
| Janvi | F | en-IN | indian-english | Steady Agent | `7ea5e9c2-b719-4dc3-b870-5ba5f14d31d8` |
| Kiara | F | en-IN | indian-english | Joyful Woman | `f8f5f1b2-f02d-4d8e-a40d-fd850a487b3d` |
| Krishna | M | en-IN | indian-english | Friendly Pal | `c63361f8-d142-4c62-8da7-8f8149d973d6` |
| Priya | F | en-IN | indian-english | Trusted Operator | `f6141af3-5f94-418c-80ed-a45d450e7e2e` |
| Sameer | M | en-IN | indian-english | Problem Solver | `638efaaa-4d0c-442e-b701-3fae16aad012` |
| Simi | F | en-IN | indian-english | Support Specialist | `3b554273-4299-48b9-9aaf-eefd438e3941` |
| Hana | F | en-NZ | new-zealand | Easygoing Support | `db408a93-859c-4a0a-b6a2-220c074cc90d` |
| Harper | F | en-NZ | new-zealand | Conversationalist | `c5d00dfb-501f-43f3-8e79-c810d24f5acd` |
| Maia | F | en-NZ | new-zealand | Agile Support | `5a033900-2ed6-4fd4-a257-707f2688e713` |
| Ruby | F | en-NZ | new-zealand | Helpful Handler | `ed9ccfa4-8fa1-40f8-bfb2-cb7d67d2f9cd` |
| Tamsin | F | en-NZ | new-zealand | Engaging Narrator | `24894159-1d4e-4b7c-80ca-4ae37dce9400` |
| Willow | F | en-NZ | new-zealand | Approachable Ally | `5f621418-ab01-4bf4-9a9d-73d66032234e` |
| Darren | M | en-SG | singaporean | Methodical Advisor | `2bc8e99c-bf1c-4977-93ff-151d7383921c` |
| Justin | M | en-SG | singaporean | Logistics Liaison | `df38a4f6-5d10-4fe7-b268-952aef25d76a` |
| Kiran | M | en-SG | singaporean | Steady Advisor | `ac5a9529-3965-4eac-b574-dce63664fbf4` |
| Nadia | F | en-SG | singaporean | Singaporean Female | `efddb3d2-4464-45e0-9f8a-fcd5fd4fc54f` |
| Sheryl | F | en-SG | singaporean | Warm Briefing | `cfce9402-0067-458b-95a7-95846f469406` |
| Adrian | M | en-US | general-american | Explorer | `e2d48e7b-cd73-4c4c-bc1e-f232580e8709` |
| Aiden | M | en-US | general-american | Yogi | `3ccc4544-84f7-45e3-ae57-5c52b5a1fac6` |
| Aina | F | en-US | general-american | Meditation Guru | `80c81aee-b6ad-4d12-9af8-a9c79c2e141d` |
| Albert | M | en-US | general-american | Firm Guide | `9a0894a9-28f0-436e-9a1d-e92bccbce4dd` |
| Allen | M | en-US | general-american | Modern Voice | `9287676d-f0cc-423f-ac03-3b3c7242f091` |
| Allie | F | en-US | general-american | Natural Conversationalist | `2747b6cf-fa34-460c-97db-267566918881` |
| Amanda | F | en-US | general-american | Warm Guide | `b60048c2-abb5-43fa-b403-90dce232e55e` |
| Amber | F | en-US | general-american | Warm Support Agent | `a7a59115-2425-4192-844c-1e98ec7d6877` |
| Ariana | F | en-US | general-american | Kind Friend | `ec1e269e-9ca0-402f-8a18-58e0e022355a` |
| Ariane | F | en-US | general-american | Captivating Tone | `1f575487-6f3d-40e0-862a-814f55b5fb15` |
| Arvin | M | en-US | general-american | Reliable Guide | `3f04e815-3260-4f50-8fd9-af9c657be4c2` |
| Asher | M | en-US | general-american | Podcaster | `00967b2f-88a6-4a31-8153-110a92134b9f` |
| Aubrey | F | en-US | general-american | Easygoing Pal | `87041166-c212-4838-9028-05d7437df750` |
| Aurora | F | en-US | general-american | Fairy Princess | `8f091740-3df1-4795-8bd9-dc62d88e5131` |
| Austin | M | en-US | general-american | Conversational Guide | `1fcd23d0-bf12-4896-8f60-4f21ef5c9b98` |
| Avery | F | en-US | general-american | Gaming Girl | `cccc21e8-5bcf-4ff0-bc7f-be4e40afc544` |
| Ben | M | en-US | general-american | Helpful Man | `bbee10a8-4f08-4c5c-8282-e69299115055` |
| Benji | M | en-US | general-american | Joyful Spirit | `2d5b8c3a-116c-4741-acaf-ba4fa289eba2` |
| Betty | F | en-US | southern-us | Reassured Guide | `fdd6abff-902a-4885-9f5f-0d3d9f7567e5` |
| Blake | M | en-US | general-american | Helpful Agent | `a167e0f3-df7e-4d52-a9c3-f949145efdab` |
| Brandon | M | en-US | general-american | Confident Guy | `5cad89c9-d88a-4832-89fb-55f2f16d13d3` |
| Brenda | F | en-US | african-american | Host | `607167f6-9bf2-473c-accc-ac7b3b66b30b` |
| Brent | M | en-US | general-american | Steady Conversationalist | `3d808d23-cb09-4c39-8afd-528e209cba4f` |
| Brielle | F | en-US | general-american | Renewal Partner | `5241b0aa-3c09-479d-b0b8-a6ec68daef5e` |
| Brittany | F | en-US | general-american | Intense Performer | `46788d8e-cdf9-4d5c-9125-094eb2e4d44c` |
| Brooke | F | en-US | general-american | Big Sister | `e07c00bc-4134-4eae-9ea4-1a55fb45746b` |
| Bryce | M | en-US | general-american | Clear Explainer | `2948c301-9211-4112-8f36-4c3fc836ef12` |
| Caleb | M | en-US | general-american | Seasoned Pro | `b9cf5ec3-eaa4-46a5-a5b2-b0d0f22395a2` |
| Callie | F | en-US | general-american | Encourager | `00a77add-48d5-4ef6-8157-71e5437b282d` |
| Calypso | F | en-US | general-american | ASMR Lady | `03496517-369a-4db1-8236-3d3ae459ddf7` |
| Cameron | M | en-US | general-american | Chill Companion | `df872fcd-da17-4b01-a49f-a80d7aaee95e` |
| Camille | F | en-US | general-american | Friendly Expert | `55deba52-bc73-4481-ab69-9c8831c8a7c3` |
| Carl | M | en-US | general-american | Steady Storyteller | `ed82c17b-4704-4d34-be43-5d19065acdf1` |
| Carol | F | en-US | general-american | Task Coach | `bf991597-6c13-47e4-8411-91ec2de5c466` |
| Caroline | F | en-US | southern-us | Southern Guide | `f9836c6e-a0bd-460e-9d3c-f7299fa60f94` |
| Carson | M | en-US | general-american | Curious Conversationalist | `86e30c1d-714b-4074-a1f2-1cb6b552fb49` |
| Carson | M | en-US | general-american | Friendly Support | `4df027cb-2920-4a1f-8c34-f21529d5c3fe` |
| Carson | M | en-US | general-american | Sad Friendly Support | `3246e36c-ac8c-418d-83cd-4eaad5a3b887` |
| Carson | M | en-US | general-american | Friendly Support | `96c64eb5-a945-448f-9710-980abe7a514c` |
| Carson | M | en-US | general-american | Angry Friendly Support | `0b32066b-2bcc-44b9-89ab-0223a09d1606` |
| Carson | M | en-US | general-american | Scared Friendly Support | `5c43e078-5ba4-4e1f-9639-8d85a403f76a` |
| Carson | M | en-US | general-american | Surprised Friendly Support | `66f5935b-af2e-4ec9-bb3e-59112e9ddc93` |
| Carson | M | en-US | general-american | Disgusted Friendly Support | `ee8b13e7-98af-4b15-89d1-8d402be10c94` |
| Cathy | F | en-US | general-american | Coworker | `e8e5fffb-252c-436d-b842-8879b84445b6` |
| Celine | F | en-US | general-american | Soothing Presence | `ca566b43-944e-4474-b494-7d9f0695f307` |
| Cera | F | en-US | general-american | Lighthearted Muse | `3af40927-948e-429b-b92d-e2158f79fb9f` |
| Chandler | M | en-US | general-american | Easygoing Pal | `356f4a89-d056-4e2e-8c73-865fa4d3af0a` |
| Chase | M | en-US | general-american | Steady Helper | `59cb0f89-5d66-49f8-b965-f72b252789e0` |
| Chloe | F | en-US | general-american | Persuasive Lady | `f762e181-ddc7-486e-9a48-636bd7e229d4` |
| Cindy | F | en-US | general-american | Receptionist | `1242fb95-7ddd-44ac-8a05-9e8a22a6137d` |
| Cindy Baker | F | en-US | general-american | Receptionist | `f039066f-cdb7-45ed-b51d-1034ae2f04a0` |
| Clara | F | en-US | general-american | Instructor | `01eaafa9-308a-4276-a017-6ab0cf061b1f` |
| Clarence | M | en-US | general-american | Newsman | `41534e16-2966-4c6b-9670-111411def906` |
| Clark | M | en-US | general-american | Trustworthy Expert | `c78dd7ae-6692-4c44-a2a2-834e365afe60` |
| Clarkson | M | en-US | general-american | Executive Tone | `c0f43c66-9f21-4034-b485-8f1d3340d759` |
| Claudia | F | en-US | general-american | Welcoming Lady | `f80e7298-93f5-46d0-86f2-b8f29cfc88bd` |
| Clementine | F | en-US | southern-us | Hospitable Host | `4111bc29-d7ff-4a15-90db-819f7b4f7706` |
| Clint | M | en-US | general-american | Rugged Actor | `db69127a-dbaf-4fa9-b425-2fe67680c348` |
| Clyde | M | en-US | southern-us | Calm Narrator | `98a34ef2-2140-4c28-9c71-663dc4dd7022` |
| Colby | M | en-US | general-american | Lively Guy | `18f8d87b-0da9-4efa-b504-4580e303f7db` |
| Cole | M | en-US | midwestern-american | Clear Communicator | `3e39e9a5-585c-4f5f-bac6-5e4905c51095` |
| Colin | M | en-US | general-american | Assured Guide | `e39b9fc0-23f5-4616-962a-da99c8ccb1dc` |
| Connie | F | en-US | general-american | Candid Conversationalist | `8d8ce8c9-44a4-46c4-b10f-9a927b99a853` |
| Connor | M | en-US | general-american | Grateful Person | `92c41dd4-04aa-45de-8504-a92b40cb8818` |
| Conrad | M | en-US | general-american | Seasoned Support | `9c8880b2-ccf9-4730-b805-cea23df247d7` |
| Corey | M | en-US | general-american | Supportive Buddy | `630ed21c-2c5c-41cf-9d82-10a7fd668370` |
| Cory | M | en-US | general-american | Relaxed Voice | `41468051-3a85-4b68-92ad-64add250d369` |
| Daisy | F | en-US | general-american | Reading Girl | `32b3f3c5-7171-46aa-abe7-b598964aa793` |
| Dallas | M | en-US | southern-us | Fireside Friend | `23e9e50a-4ea2-447b-b589-df90dbb848a2` |
| Damon | M | en-US | general-american | Commanding Narrator | `dbfa416f-d5c3-4006-854b-235ef6bdf4fd` |
| Dana | F | en-US | general-american | Balanced Spirit | `cc00e582-ed66-4004-8336-0175b85c85f6` |
| Daniel | M | en-US | general-american | Modern Assistant | `47c38ca4-5f35-497b-b1a3-415245fb35e1` |
| Daphne | F | en-US | general-american | Excited Woman | `09ed0318-2f4a-41b1-abe5-d11da7537c31` |
| Darius | M | en-US | general-american | Engaging Narrator | `23112795-d54e-4560-9568-791a87c30201` |
| David | M | en-US | general-american | Engaging Greeter | `fd098a10-ba9e-445e-b144-be2a9f3dac02` |
| David | M | en-US | general-american | Sad Greeter | `c4e848dc-d4fd-4bc8-90ea-8525563ec0e5` |
| David | M | en-US | general-american | Curious Greeter | `b08c966e-2146-4592-99eb-3171a714a43c` |
| David | M | en-US | general-american | Scared Greeter | `a3a4fe2a-d402-41d1-be7d-28f71eda755f` |
| David | M | en-US | general-american | Disgusted Greeter | `9d2b4a7f-7ced-4fb8-b570-9ce21fb931c8` |
| David | M | en-US | general-american | Happy Greeter | `6b622a1d-906f-44af-b60c-7bef365bf124` |
| David | M | en-US | general-american | Surprised Greeter | `10d17ae0-8f64-472a-be00-f00a98c729e0` |
| David | M | en-US | general-american | Greeter | `da69d796-4603-4419-8a95-293bfc5679eb` |
| Dean | M | en-US | general-american | Laidback Pal | `90c896fa-aaa1-41af-a612-5267636440a3` |
| Denise | F | en-US | general-american | Professional Woman | `8a1b8af0-c4f6-423f-a268-5507fd4aefdf` |
| Derek | M | en-US | general-american | Deep Advisor | `68fb6747-b6ea-4c44-a18e-4e29921424d3` |
| Derrick | M | en-US | general-american | Professional Man | `5cf0e4d9-ca2b-4fd5-81fa-89db3b645539` |
| Devin | M | en-US | general-american | Relaxed Spirit | `87a983d8-3471-4c4b-9ade-f1d10a4110ac` |
| Diana | F | en-US | general-american | Gentle Mom | `ea93f57f-7c71-4d79-aeaa-0a39b150f6ca` |
| Diana | F | en-US | general-american | Animated Narrator | `083de431-6b5c-4b18-a2dc-264eafa205f2` |
| Dominic | M | en-US | general-american | Sportscaster | `59697755-8cfb-4ccf-9da4-f2201d06b067` |
| Donny | M | en-US | general-american | Steady Presence | `d709a7e8-9495-4247-aef0-01b3207d11bf` |
| Doreen | F | en-US | southern-us | Decisive Coordinator | `c0832d40-57c5-4a34-991a-907b2cf0bfbf` |
| Doris | F | en-US | general-american | Friend | `0c8ed86e-6c64-40f0-b252-b773911de6bb` |
| Dorothy | F | en-US | general-american | Easy Charm | `66c6b81c-ddb7-4892-bdd5-19b5a7be38e7` |
| Dottie | F | en-US | general-american | Sweet Gal | `e3827ec5-697a-4b7c-9704-1a23041bbc51` |
| Dylan | M | en-US | general-american | Chill Companion | `b2222537-1561-4425-8c3c-e1aca96ad853` |
| Eden | N | en-US | general-american | Clear Advisor | `83ae58a1-7e97-4b94-b03f-e4cc0a10d8af` |
| Edith | F | en-US | general-american | Matriarch | `c8605446-247c-4d39-acd4-8f4c28aa363c` |
| Edna | F | en-US | general-american | Graceful Veteran | `19e399df-5b30-4fba-9d1d-99434f993614` |
| Edric | M | en-US | general-american | Refined Mentor | `921034a2-aace-4ef7-87b1-b9bc455c9a15` |
| Edward | M | en-US | general-american | Persuasive Promoter | `5fb68a42-0ed7-46fa-8a8f-ad4b332fbf6f` |
| Elaine | F | en-US | general-american | Confident Guide | `f0377496-2708-4cc9-b2f8-1b7fdb5e1a2a` |
| Elias | M | en-US | general-american | Night Warden | `6a176356-ada1-4b48-b2ae-3a3fdd485680` |
| Eliott | M | en-US | general-american | Positive Spirit | `7a8ae0b6-504a-49af-92d3-4e7e2eb84ca1` |
| Elise | F | en-US | general-american | Helpful Voice | `64b2a604-f0de-449f-9d90-255602357c05` |
| Elizabeth | F | en-US | general-american | Manager | `248be419-c632-4f23-adf1-5324ed7dbf1d` |
| Ellen | F | en-US | general-american | Welcome Agent | `a151affa-feaa-439e-8df8-c1d3f91dc6b9` |
| Ellie Mae | F | en-US | southern-us | Friendly Companion | `8d2c9eda-31df-477a-9eb6-df6f00b82845` |
| Elliott | M | en-US | general-american | Reflective Storyteller | `7edf9efb-58fc-46ba-a648-3a00a86b111b` |
| Emily | F | en-US | general-american | Easygoing Pal | `f6ce3444-478b-4ce4-982e-bcb72dffe7aa` |
| Emma | F | en-US | general-american | Customer Care Line | `f6ff7c0c-e396-40a9-a70b-f7607edb6937` |
| Erin | F | en-US | general-american | Joyful Guide | `8918ddfe-2ad4-4cc8-a573-e020ca13f3f5` |
| Esther | F | en-US | southern-us | Gracious Helper | `1a0c6bb2-bc1b-476e-8d45-56a66300362b` |
| Evan | M | en-US | general-american | Practical Guide | `bd89603f-0efb-4721-a0c8-d10b3642acc3` |
| Evelyn | F | en-US | general-american | Peaceful Whisper | `320f7211-3dc3-4292-89b1-3661e8cac27c` |
| Faye | F | en-US | southern-us | Hospitable Neighbor | `caa06a3e-c85d-459d-a1c0-4a25eeb60aeb` |
| Garrett | M | en-US | general-american | Enthusiastic Pal | `c58bda25-abd5-4c72-97a2-4dbe049b368d` |
| Gavin | M | en-US | general-american | Friendly Vibe | `f4a3a8e4-694c-4c45-9ca0-27caf97901b5` |
| Graham | M | en-US | general-american | Assured Helper | `1628cfcd-a161-4e47-98ff-46bffa4ab290` |
| Grant | M | en-US | general-american | Friendly Support | `d46abd1d-2d02-43e8-819f-51fb652c1c61` |
| Greg | M | en-US | general-american | Supporter | `a0e99841-438c-4a64-b679-ae501e7d6091` |
| Haley | F | en-US | general-american | Engaging Friend | `cec7cae1-ac8b-4a59-9eac-ec48366f37ae` |
| Harlan | M | en-US | general-american | Vintage Tone | `a892d232-f705-40d7-bc8d-e368b295ec2a` |
| Harley | M | en-US | general-american | Comforting Voice | `fdf6303b-4cfa-4f8e-b7ae-acb398984cf9` |
| Harvey | M | en-US | general-american | Precise Liaison | `1df0b2fe-acb0-4484-8f32-9e231d9e7a90` |
| Henry | M | en-US | general-american | Plainspoken Guy | `87286a8d-7ea7-4235-a41a-dd9fa6630feb` |
| Holly | F | en-US | general-american | Joyful Presence | `aef96ff9-4578-4b5d-9744-7fb347cbe4d4` |
| Howard | M | en-US | general-american | Approachable Man | `0d42f0f6-c019-4082-b250-1c16133d1c82` |
| Hugh | M | en-US | general-american | Confident Veteran | `4cf80313-54dc-4ca9-a17c-3e5b8f68a78c` |
| Iris | F | en-US | general-american | Friendly Specialist | `c894559e-d529-4d70-a6fb-3330ecf7ef6b` |
| Isla | F | en-US | general-american | Serene Flow | `eef47c0d-cb49-4160-a4a0-6b97ed4c81e6` |
| Jace | M | en-US | general-american | Cool Conversationalist | `6776173b-fd72-460d-89b3-d85812ee518d` |
| Jacqueline | F | en-US | general-american | Reassuring Agent | `9626c31c-bec5-4cca-baa8-f8ba9e84c8bc` |
| Jake | M | en-US | general-american | Sidekick | `729651dc-c6c3-4ee5-97fa-350da1f88600` |
| James | M | en-US | general-american | Navigator | `42b39f37-515f-4eee-8546-73e841679c1d` |
| Jameson | M | en-US | general-american | Easygoing Support | `a5136bf9-224c-4d76-b823-52bd5efcffcc` |
| Jamie | F | en-US | general-american | Comforting Presence | `b5c1bab5-f036-481f-9295-4db6f06f6443` |
| Jane | F | en-US | general-american | Digital Guide | `2a17e905-8f14-4db7-9b9d-9223a8e3f278` |
| Janet | F | en-US | general-american | Sunny Speaker | `58fbaf73-d7de-4e82-a6b3-118180e7057c` |
| Janice | F | en-US | general-american | Engaging Tone | `69092565-1c93-4a88-9f2c-ac8cddaf9f65` |
| Jeremy | M | en-US | general-american | Energetic Promoter | `6cb8801d-259a-4bdc-978f-b45808d58cd3` |
| Jessica | F | en-US | general-american | Clear Communicator | `25d7abcb-4d6d-4aca-adce-8a1c85620c8b` |
| Jett | M | en-US | general-american | Helpful Pal | `bbc5d060-50e1-45a3-87ff-191b8cea3092` |
| Jewel | F | en-US | general-american | Commercial Announcer | `f39d8500-0d9b-4b8b-a080-38f5188f5892` |
| Jillian | F | en-US | general-american | Happy Spirit | `e4d5f4c4-6601-4779-bee1-b3c14d629dc6` |
| Jo | F | en-US | general-american | Go to Gal | `5abd2130-146a-41b1-bcdb-974ea8e19f56` |
| Joan | F | en-US | general-american | Messenger | `c9440d34-5641-427b-bbb7-80ef7462576d` |
| Joanie | F | en-US | general-american | Vibrant Speaker | `a7b8d8fa-f6e5-4908-900e-0c11d1d82519` |
| Joey | M | en-US | new-york | Neighborhood Guy | `34575e71-908f-4ab6-ab54-b08c95d6597d` |
| Jolene | F | en-US | southern-us | Warm Storyteller | `d1d9c946-7cfc-4378-85a4-07d09827cb7e` |
| Jordan | M | en-US | general-american | Chill Pal | `87bc56aa-ab01-4baa-9071-77d497064686` |
| Joseph | M | en-US | general-american | Empathetic Voice | `7d444628-dd13-442b-b687-71a6baf0c07e` |
| Judith | F | en-US | general-american | Poised Strength | `4d3d2e9c-14e4-4802-a8d8-bd5268a73fde` |
| Julian | M | en-US | general-american | Vibrant Voice | `5319c0b1-3dd1-4c00-b721-bfd2ec88ef56` |
| Kate | F | en-US | general-american | Practical Voice | `489b647b-5662-408f-8c95-82e26ef8d29e` |
| Katie | F | en-US | general-american | Friendly Fixer | `f786b574-daa5-4673-aa0c-cbe3e8534c02` |
| Kayla | F | en-US | general-american | Easygoing Pal | `1ac31ebd-9113-405b-9d80-4a4bbbeea91c` |
| Keith | M | en-US | general-american | Easygoing Friend | `9fa83ce3-c3a8-4523-accc-173904582ced` |
| Kelly | F | en-US | general-american | Friendly Spirit | `4b1e0bf9-53a0-4e9e-8664-ba1314dbcb38` |
| Kelsey | F | en-US | general-american | Ball of energy | `050f5a7a-9d2b-4b76-84e3-2d056a0a3eb0` |
| Kendra | F | en-US | southern-us | Smooth Communicator | `358e650d-ac0b-4a74-b14f-aca3daa40d79` |
| Kenneth | M | en-US | general-american | Friendly Rep | `911b8b22-887f-4caf-bf87-85d834c08708` |
| Kiefer | M | en-US | general-american | Assured Tone | `228fca29-3a0a-435c-8728-5cb483251068` |
| Kim | F | en-US | general-american | Cheerful Pal | `eb649460-7e23-43bc-ad20-0a7a2749b938` |
| Kira | F | en-US | general-american | Trusted Confidant | `57dcab65-68ac-45a6-8480-6c4c52ec1cd1` |
| Kurt | M | en-US | general-american | Phone Support | `efa653e5-314d-46ca-9f90-70ac7d6ca71e` |
| Kyle | M | en-US | general-american | Approachable Friend | `c961b81c-a935-4c17-bfb3-ba2239de8c2f` |
| Lacey | F | en-US | general-american | Sunny Soul | `efc5488b-5429-4e72-aaa2-570981cf47d9` |
| Laurel | F | en-US | general-american | Caring Sister | `cb6a8744-41b0-4cdc-b643-fabeb545c6a9` |
| Lauren | F | en-US | general-american | Lively Narrator | `a33f7a4c-100f-41cf-a1fd-5822e8fc253f` |
| Lawson | M | en-US | general-american | Suave Storyteller | `d2c66146-c1c8-4c3a-9870-38e5a6b72442` |
| Layla | F | en-US | general-american | Casual Friend | `999df508-4de5-40a7-8bd3-8c12f678c284` |
| Leo | M | en-US | general-american | Genuine Companion | `0834f3df-e650-4766-a20c-5a93a43aa6e3` |
| Levi | M | en-US | general-american | Steady Spokesman | `4703c250-66e4-4682-a223-0a60acafcfc0` |
| Lexi | F | en-US | general-american | Fun Friend | `56b87df1-594d-4135-992c-1112bb504c59` |
| Lila | F | en-US | general-american | Meditation Guide | `4af7c703-f2a9-45dd-a7fd-724cf7efc371` |
| Lily | F | en-US | general-american | Casual Pal | `dda51133-5d43-4a3b-84e6-e68c13f60cba` |
| Linda | F | en-US | general-american | Conversational Guide | `829ccd10-f8b3-43cd-b8a0-4aeaa81f3b30` |
| Lindsey | F | en-US | general-american | Relaxed Rep | `a38e4e85-e815-43ab-acf1-907c4688dd6c` |
| Lira | F | en-US | general-american | Tranquil Voice | `c1b9a03e-747f-40ad-8e7b-18caf8aaac0b` |
| Logan | M | en-US | general-american | Approachable Friend | `ea7c252f-6cb1-45f5-8be9-b4f6ac282242` |
| Loretta | F | en-US | southern-us | Still Comfort | `25bf938a-025c-4dd0-906f-8cf8be2e26e9` |
| Luke | M | en-US | new-york | Broadway Voice | `8e14933d-ecd7-402b-9505-795130d69b35` |
| Luke | M | en-US | new-york | Disgusted Broadway Voice | `79b8126f-c5d9-4a73-8585-ba5e1a077ed6` |
| Luke | M | en-US | new-york | Surprised Broadway Voice | `725d43d6-1196-480e-bd87-728ae5eff9e1` |
| Luke | M | en-US | new-york | Scared Broadway Voice | `63426c82-a0c9-4f23-a175-50eb64c95ec1` |
| Luke | M | en-US | new-york | Angry Broadway Voice | `61001bc6-9064-40a4-b8b2-29178e0fa558` |
| Luke | M | en-US | new-york | Sad Broadway Voice | `5c7b66c2-3b58-464d-8a12-093410a269c5` |
| Luke | M | en-US | new-york | Happy Broadway Voice | `3d79b1fd-daaa-439c-bff3-903dc18e7684` |
| Luke | M | en-US | new-york | Broadway Voice | `7b2c0a2e-3dd3-4a44-b16b-26ecd8134279` |
| Lulu | F | en-US | general-american | Madame Mischief | `e13cae5c-ec59-4f71-b0a6-266df3c9bb8e` |
| Madison | F | en-US | general-american | Surprised Best Friend | `a5def41e-2e73-433f-92f7-5f1d99fef05d` |
| Madison | F | en-US | general-american | Curious Best Friend | `98c87826-dba2-44f4-b123-4c7e3c8a2647` |
| Madison | F | en-US | general-american | Happy Best Friend | `62305e79-9d39-4643-b003-5e0b096fe4f4` |
| Madison | F | en-US | general-american | Disgusted Best Friend | `5993c2c9-5d59-403e-b459-946c8b302086` |
| Madison | F | en-US | general-american | Scared Best Friend | `30236d07-62d0-4c63-abf7-df46aa45e473` |
| Madison | F | en-US | general-american | Sad Best Friend | `27c12970-3efb-4f39-a78a-2fbb7bddc941` |
| Madison | F | en-US | general-american | Best Friend | `134838f5-ce7e-4876-ac32-6367b99daf83` |
| Madison | F | en-US | general-american | Best Friend | `02fe5732-a072-4767-83e3-a91d41d274ca` |
| Maeve | F | en-US | general-american | Steady Host | `02a924f6-bb49-4177-8fbb-52238c5056d6` |
| Marcus | M | en-US | general-american | Reliable Guy | `9301949d-b7cd-40d9-a246-5a4430992d6b` |
| Marge | F | en-US | general-american | Seasoned Grace | `a2364c9d-1fe3-4553-9eff-100c4fe5ffc8` |
| Marian | F | en-US | general-american | Poised Narrator | `26403c37-80c1-4a1a-8692-540551ca2ae5` |
| Marilyn | F | en-US | general-american | Explainer | `f9fc912e-52f0-448a-8bfa-47e9ca75f25a` |
| Marjorie | F | en-US | general-american | Encouraging Aunt | `3d9b50f9-10c5-4026-9ae1-c4a698f67fc5` |
| Mark | M | en-US | general-american | Promotion Lead | `5619d38c-cf51-4d8e-9575-48f61a280413` |
| Marvin | M | en-US | general-american | Steady Ally | `49808e4c-998a-40a8-b2ea-8ac8e8ce779e` |
| Mary | F | en-US | general-american | Nurse | `5c42302c-194b-4d0c-ba1a-8cb485c84ab9` |
| Mason | M | en-US | general-american | Calm Vibe | `b58b6b46-1a27-46ba-8648-bc203a5d394e` |
| Matt | M | en-US | general-american | Goofy Friend | `bfd3644b-d561-4b1c-a01f-d9af98cb67c0` |
| Maxine | F | en-US | general-american | Relaxed Energy | `6fbca103-0f7f-4e49-97ed-49a53b4f3534` |
| Maya | F | en-US | general-american | Easygoing Ally | `cbaf8084-f009-4838-a096-07ee2e6612b1` |
| Melanie | F | en-US | general-american | Lively Spirit | `dcc82bcd-647e-4478-955f-8232d5122f8b` |
| Melina | F | en-US | general-american | Bright Spirit | `d6b0c62a-c7ff-477c-9a1f-eadd64b94360` |
| Michelle | F | en-US | general-american | Empathetic Voice | `d7bf7d75-64b7-4c1e-86c0-79d647366587` |
| Mindy | F | en-US | general-american | Spirited Ally | `d6905573-8e91-4e32-b103-fd4d1205cd87` |
| Molly | F | en-US | general-american | Upbeat Conversationalist | `03b1c65d-4b7f-4c09-91a8-e2f6f78cb2c9` |
| Monica | F | en-US | general-american | Emotive Voice | `1b4ea5fb-b1c0-43ee-a7be-4e315878c2b1` |
| Morgan | F | en-US | southern-us | Executive Expert | `0ee8beaa-db49-4024-940d-c7ea09b590b3` |
| Natalie | F | en-US | general-american | Caring Specialist | `b87d697c-0af2-4617-a72f-a17444b32d1b` |
| Natasha | F | en-US | general-american | Upbeat Guide | `e2d08065-b658-466b-ad52-cef8ee21d307` |
| Nathan | M | en-US | general-american | Easy Talker | `97f4b8fb-f2fe-444b-bb9a-c109783a857a` |
| Noah | M | en-US | general-american | Calming Presence | `a924b0e6-9253-4711-8fc3-5cb8e0188c94` |
| Nolan | M | en-US | general-american | Expressive Agent | `65209f8e-6140-4a20-b819-3cc2e21da19b` |
| Nora | F | en-US | general-american | Calm Companion | `f4c1a0b2-669d-403f-b440-4b34b34856aa` |
| Orin | M | en-US | general-american | Velvet Gentleman | `4c2dcd38-5608-45ca-8f11-51c88208d01c` |
| Parker | M | en-US | general-american | Supportive Pal | `30894953-bcce-41fe-892c-15ce19c843ff` |
| Patricia | F | en-US | general-american | Veteran Support | `e5a6cd18-d552-4192-9533-82a08cac8f23` |
| Pearl | F | en-US | southern-us | Calm Solutionist | `d6c52d6f-6478-47a2-ad54-dbc8f3335a2b` |
| Preston | M | en-US | general-american | Relatable Pal | `cd6256ef-2b2a-41f6-a8d8-c1307af5061f` |
| Quinn | F | en-US | general-american | Calm Authority | `045f0292-0731-4a4c-971d-64594fc2c35a` |
| Rachel | F | en-US | general-american | Polished Presence | `10bd4af4-825b-49b8-b8bd-0ca11865536e` |
| Ralph | M | en-US | general-american | Dynamic Commentator | `1ce291a1-0771-4732-a3f7-8cca29bf055f` |
| Ray | M | en-US | midwestern-american | Conversationalist | `565510e8-6b45-45de-8758-13588fbaec73` |
| Rebecca | F | en-US | general-american | Counselor | `57b6bf63-c7a1-4ffc-8e10-23bf45152dd6` |
| Reed | M | en-US | general-american | Polished Professional | `533b2990-5b82-45a4-b9f2-367776972ca6` |
| Reese | F | en-US | general-american | Warm Companion | `c7c790c5-2bf4-47e4-bc83-5f43e61f3803` |
| Reflective Woman | F | en-US | general-american | - | `a3520a8f-226a-428d-9fcd-b0a4711a6829` |
| Regis | M | en-US | general-american | News Anchor | `74f42072-6245-4fe2-b5dc-3dc9b56fdbd0` |
| Renee | F | en-US | general-american | Commander | `c2ac25f9-ecc4-4f56-9095-651354df60c0` |
| Riley | F | en-US | california | Chill Friend | `21b81c14-f85b-436d-aff5-43f2e788ecf8` |
| Romeo | M | en-US | general-american | Calm Narrator | `f688c0a6-dddd-48ba-8246-c099d494a162` |
| Ronald | M | en-US | general-american | Thinker | `5ee9feff-1265-424a-9d7f-8e4d431a12c7` |
| Ronan | M | en-US | general-american | Warm Buddy | `8d7d11ff-d985-48a2-a737-1da0b6fedc8b` |
| Rory | F | en-US | general-american | Maternal Vibe | `9329fbdb-e285-4fba-95ec-592e15f14476` |
| Ross | M | en-US | general-american | Reliable Partner | `f24ae0b7-a3d2-4dd1-89df-959bdc4ab179` |
| Rowan | M | en-US | general-american | Team Leader | `701a96e1-7fdd-4a6c-a81e-a4a450403599` |
| Ruth | F | en-US | midwestern-american | Manager | `11af83e2-23eb-452f-956e-7fee218ccb5c` |
| Sabrina | F | en-US | general-american | Casual Ally | `0a9a5903-0a30-4d2e-b6b6-891f73d4b4e0` |
| Samantha | F | en-US | general-american | Support Leader | `f4e8781b-a420-4080-81cf-576331238efa` |
| Samantha | F | en-US | general-american | Sad Support Leader | `5e10a334-7fa5-46d4-a64b-5ae6185da3fd` |
| Samantha | F | en-US | general-american | Happy Support Leader | `761afc95-bef5-44dd-aa07-d3c678912e43` |
| Samantha | F | en-US | general-american | Yelling Support Leader | `d3e03deb-5439-4203-add1-ca9a7501eaa7` |
| Samantha | F | en-US | general-american | Angry Support Leader | `04bfd756-4fd4-42c2-9ccf-37f647c5bf54` |
| Sarah | F | en-US | general-american | Mindful Woman | `694f9389-aac1-45b6-b726-9d9369183238` |
| Sasha | F | en-US | general-american | Cool Friend | `3f38cbe2-ce6a-4051-b5dc-2b2ee20b9bc1` |
| Savannah | F | en-US | southern-us | Magnolia Belle | `78ab82d5-25be-4f7d-82b3-7ad64e5b85b2` |
| Scott | M | en-US | general-american | Sportscaster | `2f22b9bc-b0eb-4cb6-b5ae-0c099a0fdfad` |
| Sean | M | en-US | general-american | Steady Companion | `1cb5b8bc-77c9-4e7c-a251-da02348e2727` |
| Selene | F | en-US | general-american | Soothing Aura | `63927f41-9616-4ac2-89cf-f3afa346e0ef` |
| Serena | F | en-US | general-american | Laidback Girl | `3ef78ba6-9aaa-46a2-b5b5-f9ded76a2370` |
| Shane | M | en-US | general-american | Helpful Guide | `8cbfe3ab-8364-4e72-b606-93f749519c66` |
| Sheldon | M | en-US | general-american | Help Desk Man | `39b376fc-488e-4d0c-8b37-e00b72059fdd` |
| Shelly | F | en-US | general-american | Warm Companion | `0d2162c2-2fe9-40a7-b3c1-43eab576a64b` |
| Sienna | F | en-US | general-american | Encourager | `4e41a434-85fc-4614-b203-af79ba44d473` |
| Sierra | F | en-US | california | California Girl | `b7d50908-b17c-442d-ad8d-810c63997ed9` |
| Silas | M | en-US | general-american | Nighttime Narrator | `7e19344f-9f17-47d7-a13a-4366ad06ebf3` |
| Skylar | F | en-US | general-american | Friendly Guide | `db6b0ed5-d5d3-463d-ae85-518a07d3c2b4` |
| Skyler | M | en-US | general-american | Laidback Partner | `01fd7d67-d2a0-4e4e-8c48-42611c71a926` |
| Sofía | F | en-US | southern-us | Service Navigator | `9f14cf59-e7e2-4783-b733-dbae49640789` |
| Sophie | F | en-US | general-american | Teacher | `bf0a246a-8642-498a-9950-80c35e9276b5` |
| Stephanie | F | en-US | southern-us | Steady Professional | `6a73e45f-3fa6-427c-97da-0fc6a7a1bc0d` |
| Sterling | M | en-US | general-american | Monarch | `b134c304-d095-4d2b-a77a-914f5e8e84e7` |
| Steve | M | en-US | african-american | Disgusted Baritone | `f96dc0b1-7900-4894-a339-81fb46d515a7` |
| Steve | M | en-US | african-american | Curious Baritone | `c1c65fc2-528a-4dde-a2c4-f822785c2704` |
| Steve | M | en-US | general-american | Scared Baritone | `b1ce5126-4d08-42c3-adef-d3eb39e90c7a` |
| Steve | M | en-US | general-american | Happy Baritone | `adde00e9-c98f-42ae-a94d-fc9f92f11c76` |
| Steve | M | en-US | general-american | Sad Baritone | `80713a53-e484-4f69-9852-7891096016ac` |
| Steve | M | en-US | african-american | Angry Baritone | `7c8ba972-4960-4c43-bea0-8178e2205696` |
| Steve | M | en-US | general-american | Surprised Baritone | `6fd4f468-0345-4f41-81d0-3f48ebc295e0` |
| Steve | M | en-US | african-american | Baritone | `9fb269e7-70fe-4cbe-aa3f-28bdb67e3e84` |
| Steven | M | en-US | general-american | Big Brother | `17488b72-f815-44d8-bdd9-869971c3ec06` |
| Sunny | F | en-US | general-american | Pep Talker | `156fb8d2-335b-4950-9cb3-a2d33befec77` |
| Tabitha | F | en-US | general-american | Smooth Energy | `b56c6aac-f35f-46f7-9361-e8f078cec72e` |
| Tanner | M | en-US | general-american | Upbeat Assistant | `710feaa3-b550-42f3-b3eb-6f37f2a7cc0a` |
| Tanner | M | en-US | general-american | Laidback Spirit | `373e661a-f0ef-4e34-a09e-183184a443e6` |
| Tara | F | en-US | general-american | Confident Ally | `3308b492-50cc-417e-89dd-1f446c574546` |
| Tessa | F | en-US | general-american | Kind Companion | `6ccbfb76-1fc6-48f7-b71d-91ac6298247b` |
| Theo | M | en-US | general-american | Modern Narrator | `79f8b5fb-2cc8-479a-80df-29f7a7cf1a3e` |
| Tiffany | F | en-US | general-american | Dynamic Presence | `86600680-b836-41e1-9916-8475728dcc14` |
| Tim | M | en-US | general-american | Pal | `146485fd-8736-41c7-88a8-7cdd0da34d84` |
| Tina | F | en-US | general-american | Customer Ally | `91b4cf29-5166-44eb-8054-30d40ecc8081` |
| Todd | M | en-US | general-american | Matter of Fact Salesman | `efd255c7-f030-43d3-b5d8-c7b72063be70` |
| Travis | M | en-US | southern-us | How To Guide | `40104aff-a015-4da1-9912-af950fbec99e` |
| Troy | M | en-US | southern-us | Fix It Man | `726d5ae5-055f-4c3d-8355-d9677de68937` |
| Tyler | M | en-US | general-american | Friendly Salesman | `820a3788-2b37-4d21-847a-b65d8a68c99a` |
| Valerie | F | en-US | african-american | Support Authority | `af346552-54bf-4c2b-a4d4-9d2820f51b6c` |
| Vicky | F | en-US | general-american | Businesswoman | `643f5eee-459d-4b41-b4fc-0b8407139be6` |
| Vivian | F | en-US | general-american | Fierce Narrator | `ca31ce53-ebf6-4e51-b87d-2f65d5d1f7f8` |
| Wade | M | en-US | southern-us | Southern Soul | `3d83e30f-c31b-4f26-b442-7075feafa53a` |
| Wade 2.0 | M | en-US | general-american | Southern Soul | `fbf7d2ec-ebea-49f2-8889-a482b9b0a7ed` |
| Wang | M | en-US | general-american | Guide | `79bfcec0-720c-41f2-a33a-f12383e9627f` |
| Warren | M | en-US | general-american | Seasoned Pragmatist | `aec42b73-8c46-4528-a377-537b5ecb8e7b` |
| Wes | M | en-US | general-american | Customer Companion | `2a4d065a-ac91-4203-a015-eb3fc3ee3365` |
| Wesley | M | en-US | general-american | Chill Flow | `6fccb471-26f7-4f7a-93dd-542935db6c20` |
| Whitney | F | en-US | general-american | Composed Concierge | `f3c7d5d2-c1e1-41a0-bd88-8b5512be5335` |
| Wyatt | M | en-US | southern-us | Dependable Dispatcher | `5fc5c797-12c5-4f2b-ac9b-d4e53c08098f` |
| Yasmin | F | en-US | arabic-english | Dialogue Anchor | `daf747c6-6bc2-4083-bd59-aa94dce23f5d` |
| Zack | M | en-US | general-american | Sportsman | `ed81fd13-2016-4a49-8fe3-c0d2761695fc` |
| Zander | M | en-US | general-american | Energetic Announcer | `afb19d1b-4044-4f34-a962-f4aef640a002` |
| Zeke | M | en-US | general-american | Friendly Sidekick | `e00d0e4c-a5c8-443f-a8a3-473eb9a62355` |
| Zoey | F | en-US | general-american | Bright Voice | `48369ca9-0645-40de-9821-0d55e18a03c2` |
| Anele | F | en-ZA | south-african | Bright Presenter | `072d954b-8379-4b6b-816a-bb0cd38725f8` |
| Johan | M | en-ZA | south-african | Deep Consultant | `4b31d090-8d2d-4bcd-8a32-1c135301e26e` |
| Lindiwe | F | en-ZA | south-african | Capable Professional | `8d673f7e-4a22-47fd-973a-ead9a85b7187` |
| Naledi | F | en-ZA | south-african | Engaging Instructor | `7348f896-8516-4382-9c8f-ad2aee1ffedc` |
| Nandi | F | en-ZA | south-african | Poised Concierge | `33d406dd-ff6f-4be7-a7f5-8b1ba183b3e4` |
| Pieter | M | en-ZA | south-african | Polished Analyst | `baf84392-fa95-4d44-8871-d32ee36b0e01` |
| Shana | F | en-ZA | south-african | Composed Consultant | `548172e3-7581-406b-8788-f5346fb992de` |
| Thandi | F | en-ZA | south-african | Direct Dispatcher | `692846ad-1a6b-49b8-bfc5-86421fd41a19` |
| Tristan | M | en-ZA | south-african | Calm Authority | `56c7989e-7a5f-4d12-838f-e0f910e7356e` |
| Zander | M | en-ZA | south-african | Composed Advisor | `aa2cafe9-97ba-4052-ac3c-875000f95212` |
| Zanele | F | en-ZA | south-african | Vibrant Advocate | `263b9cc0-0d99-44e7-ae92-3d4ad5d2ad18` |
| Carlo | M | it-IT | standard-italian | Roman Guide | `1fc31370-81b1-4588-9c1a-f93793c6e01d` |

## 5. Sources

- Pricing: <https://cartesia.ai/pricing>, <https://docs.cartesia.ai/pricing>
- Models and API: <https://docs.cartesia.ai/build-with-cartesia/tts-models/latest>
- Deployments: <https://www.cartesia.ai/deployments>
