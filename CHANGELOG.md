# CHANGELOG



## v0.2.0 (2024-06-03)

### Chore

* chore: use variable instead of constant in setup.cfg (#22)

Co-authored-by: ds-sebastian-chwilczynski &lt;sebastian.chwilczynski@gdeepsense.ai&gt; ([`3745054`](https://github.com/deepsense-ai/db-ally/commit/3745054379c322c515a0c4e8a89e41d2bbb38c73))

* chore: cleanup after release process ([`1bf88e9`](https://github.com/deepsense-ai/db-ally/commit/1bf88e9367259802317254c03aff884cd1cfdd27))

### Documentation

* docs: update guides and API refs (#38) ([`bc912c1`](https://github.com/deepsense-ai/db-ally/commit/bc912c11744a6f4c60e87185342ba963a0783369))

* docs: update roadmap ([`adfd479`](https://github.com/deepsense-ai/db-ally/commit/adfd479a6bc47539395ddaaf625d7333488f874b))

### Feature

* feat: freeform text2sql with static configuration (#36)

---------

Co-authored-by: Ludwik Trammer &lt;ludwik.trammer@deepsense.ai&gt;
Co-authored-by: Michał Pstrąg &lt;michal.pstrag@icloud.com&gt; ([`8f7a166`](https://github.com/deepsense-ai/db-ally/commit/8f7a166693c184631290f51e7906ccfb49acf2c9))

* feat: Add elastic store (#34)

* add elastic search store
* feat add vector search store
* update documentation ([`edd6de9`](https://github.com/deepsense-ai/db-ally/commit/edd6de9b4a9ece45514208a0dfde854607023194))

* feat(embedding): add litellm embeddings (#37) ([`2fb275f`](https://github.com/deepsense-ai/db-ally/commit/2fb275f0668fb7f981d21a6eaeae0b5effcb4acd))

* feat(llm): integrate LLMClient with litellm (#35) ([`c06b11d`](https://github.com/deepsense-ai/db-ally/commit/c06b11df1afb0c8f536c06d2f4d3d83cfc53d1d6))

* feat(audit): add audit events for SimilarityIndexes (#33)

* feat(audit): add audit events for SimilarityIndexes

* Apply suggestions from code review

Co-authored-by: Michał Pstrąg &lt;michal.pstrag@icloud.com&gt;

---------

Co-authored-by: Michał Pstrąg &lt;michal.pstrag@icloud.com&gt; ([`59e08ac`](https://github.com/deepsense-ai/db-ally/commit/59e08ac7e72fa4f946c7229872fea70d277ef411))

### Fix

* fix: AttributeError in LangSmithEventHandler (#32) ([`c8cfe97`](https://github.com/deepsense-ai/db-ally/commit/c8cfe9759aa4beb6c3bea4ae519be4b4fd2b105a))

### Refactor

* refactor(views): api for freeform views  (#41) ([`6d6cdcd`](https://github.com/deepsense-ai/db-ally/commit/6d6cdcd7a4dc6d6ea296e4483afe4cb5e24f2613))

* refactor: refactor prompt builder (#30) ([`61f1066`](https://github.com/deepsense-ai/db-ally/commit/61f10669c29575178817cd9766f3e8cc4f16c79f))

* refactor: add LLMOptions merge (#29) ([`7191c3f`](https://github.com/deepsense-ai/db-ally/commit/7191c3fbdeb0e10867e4daeaab27cf45fee28368))

* refactor: refactor LLMOptions (#28) ([`3f5c4bf`](https://github.com/deepsense-ai/db-ally/commit/3f5c4bff2dcb0d354a744f1a7291e0f08a335867))

* refactor: move prompt templates to modules which use them (#26)

* move prompt templates to modules which use them
* reorganize imports ([`e0f17a7`](https://github.com/deepsense-ai/db-ally/commit/e0f17a79f098549c4d98225101d5aa92733e503e))

* refactor: add monotonic clock (#25) ([`9b31299`](https://github.com/deepsense-ai/db-ally/commit/9b31299c5da9dc563beaff9762f2e85ed7bc1c4e))


## v0.1.0 (2024-04-25)

### Documentation

* docs(views): add documentation of freeform views (#21)

Add documentation of freeform views, comparision of structured &amp; freeform views.

---------

Co-authored-by: Mateusz Hordyński &lt;mateusz.hordynski@deepsense.ai&gt;
Co-authored-by: Mateusz Hordyński &lt;26008518+mhordynski@users.noreply.github.com&gt; ([`668b2ce`](https://github.com/deepsense-ai/db-ally/commit/668b2cea6bf1c1497e30121f55f9dcba1d546c7c))

* docs: minor issues with classes names (#19)

Co-authored-by: ds-sebastian-chwilczynski &lt;sebastian.chwilczynski@gdeepsense.ai&gt; ([`4a26cbb`](https://github.com/deepsense-ai/db-ally/commit/4a26cbbb676016d1059273a8ab7a59fa40048bb9))

### Feature

* feat: add text2sql freeform view (#20)

Add new freeform view: text2sql - direct creation of SQL query to answer user question together with initial setup of database discovery. ([`d6dc713`](https://github.com/deepsense-ai/db-ally/commit/d6dc7131fd2c55dbd0361d801bd1a97510b81733))

* feat(views): allow for freeform views (#15)

Ground work for supporting a new type of views: freeform.
Freeform views are not bounded by IQL and can answer natural language questions directly. ([`61ab8c9`](https://github.com/deepsense-ai/db-ally/commit/61ab8c9147dc07bb819fd411158f040709bee649))

* feat: automatic versioning (#16) ([`b7ffa25`](https://github.com/deepsense-ai/db-ally/commit/b7ffa255981ba3f5f22f7445a6d6415863575cdf))

### Fix

* fix: add exception handling to LangGraph notebook

Co-authored-by: ds-sebastian-chwilczynski &lt;sebastian.chwilczynski@gdeepsense.ai&gt; ([`6b607d6`](https://github.com/deepsense-ai/db-ally/commit/6b607d6a8dd49e37a393d7cbc033e4c3be9da775))

### Unknown

* Feat: Integration with Chromadb (#18)

* feat: chroma db support

* fix: hash issues

* test: integration chroma testing
---------

Co-authored-by: ds-sebastian-chwilczynski &lt;sebastian.chwilczynski@gdeepsense.ai&gt;
Co-authored-by: Mateusz Hordyński &lt;26008518+mhordynski@users.noreply.github.com&gt; ([`e455d53`](https://github.com/deepsense-ai/db-ally/commit/e455d53a45eb96076a39f69329ff8d8bc8388892))


## v0.0.2 (2024-04-17)

### Fix

* fix: gitlab evaluation ([`cf80f8c`](https://github.com/deepsense-ai/db-ally/commit/cf80f8c585790c0c94d030b63a723df3ddcbe5fd))

### Unknown

* Bump version: 0.0.2-dev → 0.0.2 ([`669973a`](https://github.com/deepsense-ai/db-ally/commit/669973a73b92628667813c9b20b7a2f50ef048f4))

* Bump version: 0.0.1 → 0.0.2-dev ([`ec46c92`](https://github.com/deepsense-ai/db-ally/commit/ec46c9288898f1ad0ef9fd3329d00a6a5c039d81))

* Remove the use_* global functions (#13)

* Remove the use_* global functions

* Remove use_openai_llm from notebooks ([`e3bcf06`](https://github.com/deepsense-ai/db-ally/commit/e3bcf0672d1b90b370b60eebb0b4d8fb8b1dad16))

* Integrate tutorials with the repository. (#14)

* upload tutorials

* provide link to collab

* remove raw tutorials info

---------

Co-authored-by: ds-sebastian-chwilczynski &lt;sebastian.chwilczynski@gdeepsense.ai&gt; ([`211337d`](https://github.com/deepsense-ai/db-ally/commit/211337de286849b00981f1ec1cb0f44aa6d50191))

* API Reference refactor


---------

Co-authored-by: ds-sebastian-chwilczynski &lt;sebastian.chwilczynski@gdeepsense.ai&gt; ([`7c16a24`](https://github.com/deepsense-ai/db-ally/commit/7c16a248946ac3a990f69b989c5689dfc68c5004))

* Allow injecting dependencies in calls to create_collection (#12)

* Allow injecting dependencies in calls to create_collection

* Make the create_collection description more detailed ([`b3251df`](https://github.com/deepsense-ai/db-ally/commit/b3251df4fc7ffebfbbede165ea45e7465fdb3e0a))

* Add Collection methods to detect/update similarity indexes (#11)

* Add Collection methods to detect/update similarity indexes

* Handle exceptions during index update ([`bb53811`](https://github.com/deepsense-ai/db-ally/commit/bb53811a28be7ccb37c1abaf4ecd8dfd48075fd4))

* Use full company name in license ([`93c601d`](https://github.com/deepsense-ai/db-ally/commit/93c601dc67ee00895eff1f58715a0dd0e5dba85c))

* Fix tests (#10)

A combination of two merged commits that worked separately broke tests.

This fixes the problem. ([`7e8736f`](https://github.com/deepsense-ai/db-ally/commit/7e8736ff5f4dc5fdf42302ac44b265fc5109d417))

* Add API and CLI command for updating multiple indexes at one (#4)

* Add API and CLI command for updating multiple indexes at one

* Add documentation and additional tests ([`a2e37b5`](https://github.com/deepsense-ai/db-ally/commit/a2e37b5851ea7a64853b836231a1aa211e8d2e7a))

* Merge pull request #9 from deepsense-ai/mh/move_examples

Move examples out of dbally package ([`3191f24`](https://github.com/deepsense-ai/db-ally/commit/3191f24a390398eb0da567ffb96e87273dbe4542))

* Separate view-level and collection-level results (#8)

* Separate view-level and collection-level results

* Add tests for Collection.ask

* Add documentation ([`89062dc`](https://github.com/deepsense-ai/db-ally/commit/89062dc68c037b1f4e22377f94f405d7d0b5e3a6))

* Move examples out of dbally package ([`9b9effe`](https://github.com/deepsense-ai/db-ally/commit/9b9effe54a386073b2da73fa95872f2274664d13))

* Add validation of view builder during registration (#6) ([`74892b9`](https://github.com/deepsense-ai/db-ally/commit/74892b96361fa417677e2f08053d4d4573cceb07))

* Fix imports in README example (#5) ([`6a4c2df`](https://github.com/deepsense-ai/db-ally/commit/6a4c2dfe873d1efb58e88078b99edb756532ef44))

* Api Reference

* Add API references

* Add changes in the mkdocs.yml file

* Add changed mkdocs file

* Fix pylint

* Small fix

* Add faiss store

* Small fix

* Add LLMViewSelector

* Small fix

* Add reference docs

* start refactoring documentation

* update roadmap with assistants

---------

Co-authored-by: alicja.kotyla &lt;alicja.kotyla@deepsense.ai&gt;
Co-authored-by: Mateusz Hordyński &lt;mateusz.hordynski@deepsense.ai&gt;
Co-authored-by: ds-sebastian-chwilczynski &lt;sebastian.chwilczynski@gdeepsense.ai&gt; ([`8288802`](https://github.com/deepsense-ai/db-ally/commit/8288802a50c43a84470ccfefdbc88fbdd397b908))

* Extra configuration for docs ([`6a6a189`](https://github.com/deepsense-ai/db-ally/commit/6a6a189db74bb550bb589f2681233ace46a74514))

* Add how to guides on custom similarity fetchers nad stores (#3)

* Add how to guides on custom similarity fetchers nad stores

* Add info about async

* async -&gt; await ([`e2a4047`](https://github.com/deepsense-ai/db-ally/commit/e2a4047a4eb31fe820e9e82076c6f469e10b9e06))

* Add gcp env to docs build process ([`ee6f6ca`](https://github.com/deepsense-ai/db-ally/commit/ee6f6ca37ffe02193d572b67a8bf3f936577e53d))

* Bump version 0.0.1-dev -&gt; 0.0.1 ([`0a51910`](https://github.com/deepsense-ai/db-ally/commit/0a5191059da341af425466a116412d9bd1c0ae54))

* Add source to setup.cfg ([`0f8be41`](https://github.com/deepsense-ai/db-ally/commit/0f8be416b8d60afb67a9dfe862dc5038ec545c88))

* Change license in setup.cfg ([`82d2c79`](https://github.com/deepsense-ai/db-ally/commit/82d2c796ccff5464b955c16c47de89981771ddcf))

* Fix docs build script ([`978f45d`](https://github.com/deepsense-ai/db-ally/commit/978f45d47a5c031051cf12615fde5873924a124c))

* Fix build script ([`161d100`](https://github.com/deepsense-ai/db-ally/commit/161d100f4c3a4192a0bbd48aceaeaa14142ea5de))

* Add environment ([`e491e76`](https://github.com/deepsense-ai/db-ally/commit/e491e7623db64237d55cdf49c7e97cff56084e15))

* Docs build on GH actions ([`a468479`](https://github.com/deepsense-ai/db-ally/commit/a4684790afb3677dc346e45c0ac313d85131b6af))

* Merge pull request #1 from deepsense-ai/mh/github_actions

Setup github actions ([`7a2a7a2`](https://github.com/deepsense-ai/db-ally/commit/7a2a7a22ac169035bb0721d983cb11f3cb20b243))

* Remove gitlab ci ([`b9990b9`](https://github.com/deepsense-ai/db-ally/commit/b9990b94fc02f1446e808a851a9242c249fd420e))

* Add docs generation ([`11fd274`](https://github.com/deepsense-ai/db-ally/commit/11fd274926f4092c208168724b032c8cace131c7))

* Fix license checking ([`5abf187`](https://github.com/deepsense-ai/db-ally/commit/5abf187021debffb1b24adc17d7f5f80d28a38e9))

* Change python version in GH actions ([`4081e4a`](https://github.com/deepsense-ai/db-ally/commit/4081e4a82e517b067f6777bb809ecdd505952618))

* Fix lint ([`fa05d99`](https://github.com/deepsense-ai/db-ally/commit/fa05d996246f0f562a81ac17a703d9bca2ee4110))

* Merge branch &#39;mh/github_prep&#39; ([`44cd9ec`](https://github.com/deepsense-ai/db-ally/commit/44cd9ece37b6c7ee0effb26d2189f4144b969484))

* gh prep ([`1f89364`](https://github.com/deepsense-ai/db-ally/commit/1f89364ee593497894df669ebb6212a1d65a3483))

* gh prep ([`4278360`](https://github.com/deepsense-ai/db-ally/commit/4278360831aeeb5f85fa6f647bcfc7bee5529d1c))

* Merge branch &#39;sc/tutorial&#39; into &#39;main&#39;

Sc/tutorial

See merge request deepsense.ai/g-internal/db-ally!75 ([`d62a61d`](https://github.com/deepsense-ai/db-ally/commit/d62a61d0c82126e6415f6417e2c1fc1fb94cfeb0))

* OpenAI Assistants API tutorial ([`56206a4`](https://github.com/deepsense-ai/db-ally/commit/56206a4cf3da7be64204bf77b5032b056b54f894))

* Merge branch &#39;mh/pypi_final&#39; into mh/github_prep ([`f7eb52f`](https://github.com/deepsense-ai/db-ally/commit/f7eb52fe40273bdba64633d09bb14109b8310de9))

* Merge branch &#39;lt/dataframe&#39; into &#39;main&#39;

Introduce Pandas DataFrame base view

See merge request deepsense.ai/g-internal/db-ally!74 ([`380c4b7`](https://github.com/deepsense-ai/db-ally/commit/380c4b7de50d4cc97f67434d865770c28e779ebc))

* Introduce Pandas DataFrame base view ([`77131f1`](https://github.com/deepsense-ai/db-ally/commit/77131f103c69c93e28c212dcc3e59895ac2e74bb))

* Merge branch &#39;sc.openai_integration&#39; into &#39;main&#39;

OpenAI assistants adapter

See merge request deepsense.ai/g-internal/db-ally!69 ([`c396073`](https://github.com/deepsense-ai/db-ally/commit/c3960730b3672a04c89586cdc6f3d55b17c80aff))

* OpenAI assistants adapter ([`f96c041`](https://github.com/deepsense-ai/db-ally/commit/f96c041ec25c31834595071a1c75dd31ee351c64))

* Merge branch &#39;lt/custom_views_how_to&#39; into &#39;main&#39;

How-To: Write Custom Views

See merge request deepsense.ai/g-internal/db-ally!72 ([`dc5c8f9`](https://github.com/deepsense-ai/db-ally/commit/dc5c8f9cbd80385526cd28e5eef6575aa8f89d81))

* How-To: Write Custom Views ([`dbe3874`](https://github.com/deepsense-ai/db-ally/commit/dbe3874178fff36ca6eda576820f2a21401ea934))

* Merge branch &#39;mh/fix_docs_feedback2&#39; into &#39;main&#39;

Fix after feedback

See merge request deepsense.ai/g-internal/db-ally!73 ([`e028497`](https://github.com/deepsense-ai/db-ally/commit/e028497234c03dd70fb6a6472c2ec2f251e30b71))

* Fix after feedback ([`b26f4f1`](https://github.com/deepsense-ai/db-ally/commit/b26f4f18f194099d78eccae3e63479d5c21a5434))

* Merge branch &#39;mh/fix_transformers_dep&#39; into &#39;main&#39;

Fix transformers dependency

See merge request deepsense.ai/g-internal/db-ally!71 ([`f7d3ae2`](https://github.com/deepsense-ai/db-ally/commit/f7d3ae2fa2fbac57701a65eac65d6d025db9a0a4))

* Add transformers to dev packages ([`c76160c`](https://github.com/deepsense-ai/db-ally/commit/c76160c468bf5e05e41baae6a028f77ba1b5645d))

* Fix circular import ([`9d4cb49`](https://github.com/deepsense-ai/db-ally/commit/9d4cb494a073976ac1ea230378130966ddbb0d09))

* Fix transformers dependency ([`3e37723`](https://github.com/deepsense-ai/db-ally/commit/3e377230930110bf0667fd88659f947046a7bfe7))

* Merge branch &#39;mh/docs_dark_view&#39; into &#39;main&#39;

Add dark theme

See merge request deepsense.ai/g-internal/db-ally!68 ([`903adab`](https://github.com/deepsense-ai/db-ally/commit/903adabb9b47062da8e4bd25514ded699a646069))

* Add dark theme ([`3abba3f`](https://github.com/deepsense-ai/db-ally/commit/3abba3f4cbb445d7f9be4d7236870373c3caf1bb))

* Merge branch &#39;mh/docs_fixes_after_feedback&#39; into &#39;main&#39;

Fix links

See merge request deepsense.ai/g-internal/db-ally!67 ([`1440fa3`](https://github.com/deepsense-ai/db-ally/commit/1440fa3bb52256f7f931a60a0a73d87be49ec90d))

* IQL explained ([`49f3203`](https://github.com/deepsense-ai/db-ally/commit/49f3203d35a0e9f8fadbcc3793bcafe7a8ae6291))

* Fix links ([`ef9dff8`](https://github.com/deepsense-ai/db-ally/commit/ef9dff81a23bdfec97d7e1b2a08a68f3e55edd7a))

* Merge branch &#39;mh/clean_docs_nav&#39; into &#39;main&#39;

Remove not finished docs from nav

See merge request deepsense.ai/g-internal/db-ally!66 ([`4465cd1`](https://github.com/deepsense-ai/db-ally/commit/4465cd1f8e2e122658bf5e323341d56c958c2e2d))

* Remove not finished docs from nav ([`a3d0543`](https://github.com/deepsense-ai/db-ally/commit/a3d0543e04445f18c846864a681a2dbcd6f90855))

* Merge branch &#39;mh/roadmap&#39; into &#39;main&#39;

Add roadmap

See merge request deepsense.ai/g-internal/db-ally!65 ([`66bad62`](https://github.com/deepsense-ai/db-ally/commit/66bad629571178931ccb0cbd112b2584f53f5640))

* Apply suggestions ([`770a5cb`](https://github.com/deepsense-ai/db-ally/commit/770a5cb44239a6b103c00e52e196597addfca5e6))

* Add roadmap ([`b4e7f58`](https://github.com/deepsense-ai/db-ally/commit/b4e7f583c8774e5084b4409380fbd36f541c890c))

* Merge branch &#39;az/add-readme&#39; into &#39;main&#39;

Add readme

See merge request deepsense.ai/g-internal/db-ally!56 ([`bff2451`](https://github.com/deepsense-ai/db-ally/commit/bff245153129690a8ddc44ff37cb53611861563d))

* Fix extensions ([`52887b5`](https://github.com/deepsense-ai/db-ally/commit/52887b546848888a88b0ac355d82ddac94897b57))

* Merge branch &#39;main&#39; into az/add-readme ([`00748c9`](https://github.com/deepsense-ai/db-ally/commit/00748c94b90e54e91a0e668b4cbfb9845428a5a3))

* Fix whitespace ([`2f70004`](https://github.com/deepsense-ai/db-ally/commit/2f70004fd06de7e81c344351132518413ac0ae1b))

* Merge branch &#39;sc/tutorial&#39; into &#39;main&#39;

Tutorial

See merge request deepsense.ai/g-internal/db-ally!53 ([`e9b28b8`](https://github.com/deepsense-ai/db-ally/commit/e9b28b845057c77c2c1bd060cab579ff5d11d1ac))

* First tutorial ([`92a2479`](https://github.com/deepsense-ai/db-ally/commit/92a24792e0bbf4f7102c00125f0dbf6c6e2c0049))

* Apply 1 suggestion(s) to 1 file(s) ([`be0499d`](https://github.com/deepsense-ai/db-ally/commit/be0499dbceb53a17823211dd48206ca4a6b6aaa4))

* Add motivation and make sure that README is ready ([`26e3001`](https://github.com/deepsense-ai/db-ally/commit/26e3001e5bbdda1dde960fb3b4f8fe6d07c204d8))

* Pypi setup ([`2593cf3`](https://github.com/deepsense-ai/db-ally/commit/2593cf38df56482a58836af6c6216ad0c3abced8))

* Merge branch &#39;main&#39; into az/add-readme ([`4d7d6e1`](https://github.com/deepsense-ai/db-ally/commit/4d7d6e1f53e6c9928ebbf6e78d6282a619bda023))

* Merge branch &#39;az/add-readme&#39; into mh/pypi_final ([`5ececeb`](https://github.com/deepsense-ai/db-ally/commit/5ececeb0bc48923df441152e938d463972ba4ffd))

* Merge branch &#39;lt/how_to_sql&#39; into &#39;main&#39;

How-to: Use SQL databases with db-ally

See merge request deepsense.ai/g-internal/db-ally!63 ([`a221468`](https://github.com/deepsense-ai/db-ally/commit/a221468b1ace4b03992899fda349e20a71784cb3))

* How-to: Use SQL databases with db-ally ([`30bd21e`](https://github.com/deepsense-ai/db-ally/commit/30bd21efeefe38e866c4881484938a20743d4d7d))

* Merge branch &#39;ak/fix-typo&#39; into &#39;main&#39;

Fix typo

See merge request deepsense.ai/g-internal/db-ally!64 ([`a6fff56`](https://github.com/deepsense-ai/db-ally/commit/a6fff56725c69094c3e117622138860ccb878b02))

* Fix typo ([`b13ccfe`](https://github.com/deepsense-ai/db-ally/commit/b13ccfe2555e7250e3159965124ef0181b2b767f))

* Merge branch &#39;main&#39; into az/add-readme ([`6089736`](https://github.com/deepsense-ai/db-ally/commit/6089736c710a9d4d8907c2f8e00afa24b1467a8a))

* Merge branch &#39;ak/cleanup-package-build&#39; into &#39;main&#39;

Cleanup package build

See merge request deepsense.ai/g-internal/db-ally!62 ([`30d0a3e`](https://github.com/deepsense-ai/db-ally/commit/30d0a3e14cdf43b1c66fee3497c79a2a95807b81))

* Cleanup package build ([`4bfd0c5`](https://github.com/deepsense-ai/db-ally/commit/4bfd0c563cfab9c672379a51dfc09f106d5ee4a5))

* Merge branch &#39;mh/event_handler_docs&#39; into &#39;main&#39;

Event Handlers documentation

See merge request deepsense.ai/g-internal/db-ally!57 ([`f3d7808`](https://github.com/deepsense-ai/db-ally/commit/f3d78083afa20eb1deca06266b1c2d06a08a7d99))

* Merge branch &#39;lt/concepts&#39; into &#39;main&#39;

Documentation: concepts

See merge request deepsense.ai/g-internal/db-ally!59 ([`d532c08`](https://github.com/deepsense-ai/db-ally/commit/d532c08b918e3a8de08a0bdb0bfdbe384801a775))

* Documentation: concepts ([`2db6bbe`](https://github.com/deepsense-ai/db-ally/commit/2db6bbe92bdb0068c2854999d140d72f3ce0570f))

* Merge branch &#39;ak/nl-responder-concept&#39; into &#39;main&#39;

Add NL Responder docs

See merge request deepsense.ai/g-internal/db-ally!61 ([`57c136a`](https://github.com/deepsense-ai/db-ally/commit/57c136abc6910243dd0d7e9b7ccb9b0fc90c7563))

* Add NL Responder docs ([`e6787a6`](https://github.com/deepsense-ai/db-ally/commit/e6787a6de93480d934cc593a49bf2c92cb7f6e39))

* Fix wording ([`9f3bc95`](https://github.com/deepsense-ai/db-ally/commit/9f3bc95ffb1a379e2f28208f474abfabd05b6215))

* Add create custom event handler guide ([`5357303`](https://github.com/deepsense-ai/db-ally/commit/5357303644631b5254bb7e609b25c7e30d4be76e))

* Merge branch &#39;mh/fix_packaging&#39; into &#39;main&#39;

Add __init__ files

See merge request deepsense.ai/g-internal/db-ally!60 ([`62d9b58`](https://github.com/deepsense-ai/db-ally/commit/62d9b58f69ff2a06adbff8c1136671557a0aa28e))

* Add __init__ files ([`ea70146`](https://github.com/deepsense-ai/db-ally/commit/ea70146bf8268729017cbc65f66a39521dddbcb6))

* Merge branch &#39;ak/add-build-docs-stage&#39; into &#39;main&#39;

Build docs while running CI/CD pipeline

See merge request deepsense.ai/g-internal/db-ally!58 ([`8345e28`](https://github.com/deepsense-ai/db-ally/commit/8345e286dd5ce10e3a9b1a38ad5e071fb5939216))

* Build docs while running CI/CD pipeline ([`bd61756`](https://github.com/deepsense-ai/db-ally/commit/bd61756c31a7e796eb1ece7ec081558d1818fac7))

* Add EventHandler reference ([`dd6a231`](https://github.com/deepsense-ai/db-ally/commit/dd6a231ab2dec6d4ab1721487c969b2cc2b96b3a))

* README formatting ([`10c25d4`](https://github.com/deepsense-ai/db-ally/commit/10c25d45f4aff4a556b8841d7e7abc9bc08d0212))

* update readme file ([`45cbd17`](https://github.com/deepsense-ai/db-ally/commit/45cbd17a45a58789d20bfd3635d4e28d25f551c7))

* Add LangSmith how-to ([`e14dd0a`](https://github.com/deepsense-ai/db-ally/commit/e14dd0ab39d1c9c2b3f4c4ebe47298011b343326))

* initial readme intro ([`bf828b1`](https://github.com/deepsense-ai/db-ally/commit/bf828b131b36ff5e37a909ad73b37c6b109f2dad))

* Merge branch &#39;lt/quickstart&#39; into &#39;main&#39;

Add the Quickstart guide

See merge request deepsense.ai/g-internal/db-ally!54 ([`d022a1c`](https://github.com/deepsense-ai/db-ally/commit/d022a1c634de1b91954e0826ab9fccc2b7cc7ed4))

* Fix a typo ([`e25a91a`](https://github.com/deepsense-ai/db-ally/commit/e25a91a5560b55bcfc4b2d03d2ffc3af77a9fa99))

* Mention the tutorial ([`62f2810`](https://github.com/deepsense-ai/db-ally/commit/62f281065e6ed25ecab38e2103eace230e0c1410))

* Small improvements to the text ([`34983e0`](https://github.com/deepsense-ai/db-ally/commit/34983e04ffd900cd9473ea63cbd372e97c3a6f36))

* Merge branch &#39;main&#39; into &#39;lt/quickstart&#39;

# Conflicts:
#   mkdocs.yml ([`20c1938`](https://github.com/deepsense-ai/db-ally/commit/20c1938c2be86dcd9f9421e98f19f4edc773fa16))

* Merge branch &#39;mh/docs_nav&#39; into &#39;main&#39;

Mock docs navigation

See merge request deepsense.ai/g-internal/db-ally!55 ([`8489940`](https://github.com/deepsense-ai/db-ally/commit/84899400032aeac72d04a4954cea67ed0d042527))

* Merge branch &#39;ak/tweak-iql-prompt&#39; into &#39;main&#39;

Tweak IQL prompt (and remove actions)

See merge request deepsense.ai/g-internal/db-ally!51 ([`ad1c6ff`](https://github.com/deepsense-ai/db-ally/commit/ad1c6ffc579747cfe4e23d2e5b6e409ca09232e8))

* Tweak IQL prompt (and remove actions) ([`f5ba341`](https://github.com/deepsense-ai/db-ally/commit/f5ba341db198ede80083aa2714f590487b2bcb9e))

* Mock docs navigation ([`6be0a0c`](https://github.com/deepsense-ai/db-ally/commit/6be0a0cba040abb3154c37c89561266f1b2070d0))

* Move quickstart to a separate category ([`b455ab6`](https://github.com/deepsense-ai/db-ally/commit/b455ab6c5e252976bd9f9499ba11995c1448d77f))

* Add expected output ([`7148374`](https://github.com/deepsense-ai/db-ally/commit/71483748ba2da3b2b2dd1462f7e751947e103033))

* Review changes ([`92e24f6`](https://github.com/deepsense-ai/db-ally/commit/92e24f636e3f95b4871ad31274b16f2b5d6a24bd))

* Merge branch &#39;sc/example&#39; into &#39;main&#39;

Initial dbally example

See merge request deepsense.ai/g-internal/db-ally!49 ([`15f45b8`](https://github.com/deepsense-ai/db-ally/commit/15f45b8b55c33bbfa96f41841f8f846f4c4282a6))

* Initial dbally example ([`7259e33`](https://github.com/deepsense-ai/db-ally/commit/7259e3349e85f37f9610a790b26bf56750a369d7))

* Add the Quickstart tutorial ([`55d4699`](https://github.com/deepsense-ai/db-ally/commit/55d4699e7660fcca32dbe02f606270dcc7db012f))

* Merge branch &#39;mh/annotated_similarity&#39; into &#39;main&#39;

Annotated similarity index syntax

See merge request deepsense.ai/g-internal/db-ally!48 ([`b3cb41f`](https://github.com/deepsense-ai/db-ally/commit/b3cb41fa9575efbaae0f10364cc37f81cd49f345))

* Merge branch &#39;mh/mkdocs&#39; into &#39;main&#39;

Basic mkdocs setup

See merge request deepsense.ai/g-internal/db-ally!52 ([`d6b92a4`](https://github.com/deepsense-ai/db-ally/commit/d6b92a4f0bcd95a8a7fbb17c0c42bfa1a198fcf2))

* Basic mkdocs setup ([`f435f2e`](https://github.com/deepsense-ai/db-ally/commit/f435f2ec941614a23eb94996ca3e9c99571cc828))

* Merge branch &#39;lt/faiss&#39; into &#39;main&#39;

FAISS-based similarity store + OpenAI embedding client

See merge request deepsense.ai/g-internal/db-ally!50 ([`567191e`](https://github.com/deepsense-ai/db-ally/commit/567191ed114e1993f126bcb3f62e6a3c752af4a3))

* FAISS-based similarity store + OpenAI embedding client ([`cfcc95e`](https://github.com/deepsense-ai/db-ally/commit/cfcc95ed9e7b3bf707fc628f408743f67ab36513))

* Use Annotated from typing_extensions; parser -&gt; processor ([`6ee3e4a`](https://github.com/deepsense-ai/db-ally/commit/6ee3e4a6337bef3da9a7b78faa662fa41e371294))

* Merge branch &#39;ak/tweaks-in-nl-responder&#39; into &#39;main&#39;

Tweaks in NLResponder

See merge request deepsense.ai/g-internal/db-ally!47 ([`0504675`](https://github.com/deepsense-ai/db-ally/commit/05046750e8f5d3f444b2040736660cb045d4a9f9))

* Change function name ([`2d26d17`](https://github.com/deepsense-ai/db-ally/commit/2d26d17bae98ef653193012376430b359053c678))

* Annotated similarity for python 3.8 ([`edba405`](https://github.com/deepsense-ai/db-ally/commit/edba4059644d69b4c493abe763eeb2e67f7f0d84))

* Fix tests ([`6575eef`](https://github.com/deepsense-ai/db-ally/commit/6575eef661125606b6c7581b42446d1cb113288a))

* Undo lint fixes ([`37b6b4c`](https://github.com/deepsense-ai/db-ally/commit/37b6b4c21822501ac288dccbbae6b91d53f970f6))

* Add tweaks in NLResponder ([`8395291`](https://github.com/deepsense-ai/db-ally/commit/8395291277a77873d3de76cec6a660edbe9bbdc1))

* More changes ([`d2a7cb3`](https://github.com/deepsense-ai/db-ally/commit/d2a7cb3bf92bcf02411420dd4453fc84892ed0cd))

* Initial changes ([`37b7d04`](https://github.com/deepsense-ai/db-ally/commit/37b7d0494558cfe968c1268e659ffc28a4c6ddb8))

* Merge branch &#39;sc/fix-gitlab-test&#39; into &#39;main&#39;

fix: gitlab evaluation

See merge request deepsense.ai/g-internal/db-ally!46 ([`71e644c`](https://github.com/deepsense-ai/db-ally/commit/71e644c1893ce19f23c2e51ffbbc1dc5a2808595))

* Merge branch &#39;lt/async_views&#39; into &#39;main&#39;

Support for async indexes and views

See merge request deepsense.ai/g-internal/db-ally!45 ([`ca7f521`](https://github.com/deepsense-ai/db-ally/commit/ca7f5213df7ea6aa73cf5d0c6e88787fa4bb7206))

* Support for async indexes and views ([`df7cb0f`](https://github.com/deepsense-ai/db-ally/commit/df7cb0f55f9437f09aea5f35bd20a241f850871a))

* Merge branch &#39;lt/initial_similarity&#39; into &#39;main&#39;

Initial implementation of similarity index

See merge request deepsense.ai/g-internal/db-ally!41 ([`48e3bdb`](https://github.com/deepsense-ai/db-ally/commit/48e3bdb53128a8651d5517a5c710d495192c38d5))

* Merge branch &#39;sc/multidb_benchmarking&#39; into &#39;main&#39;

Multi-db benchmarking

See merge request deepsense.ai/g-internal/db-ally!43 ([`baf6cb8`](https://github.com/deepsense-ai/db-ally/commit/baf6cb873b4030bb40e2ae01d773228be37730cc))

* Multi-db benchmarking ([`79ac204`](https://github.com/deepsense-ai/db-ally/commit/79ac2043ba987bbf365d6815429a1ac6ee13d635))

* Merge branch &#39;lt/cli&#39; into &#39;main&#39;

Setup click-based CLI

See merge request deepsense.ai/g-internal/db-ally!44 ([`42a65a8`](https://github.com/deepsense-ai/db-ally/commit/42a65a87d090813e0241a4d37e4989fbcc2493ba))

* Setup click-based CLI ([`6874903`](https://github.com/deepsense-ai/db-ally/commit/687490308089c2752c9e41520ca25899c54093ff))

* Merge branch &#39;ak/iql-benchmark&#39; into &#39;main&#39;

IQL benchmark

See merge request deepsense.ai/g-internal/db-ally!39 ([`f90048a`](https://github.com/deepsense-ai/db-ally/commit/f90048abdf75805e18f64297ecc65861d438f4e0))

* IQL benchmark ([`f8a7b50`](https://github.com/deepsense-ai/db-ally/commit/f8a7b502b785ca3001a2f6f7c49984ca0df1620f))

* Initial implementation of similarity index ([`7f8e3dd`](https://github.com/deepsense-ai/db-ally/commit/7f8e3dd426e07e39b1bf5322a845fe28072cbbfd))

* Merge branch &#39;mh/better_iql_preprocessing&#39; into &#39;main&#39;

Better IQL preprocessing

See merge request deepsense.ai/g-internal/db-ally!38 ([`ba29bee`](https://github.com/deepsense-ai/db-ally/commit/ba29bee0b6a2d0d0094e72bd9d13cf4058448210))

* Merge branch &#39;ak/hotfix-response-format&#39; into &#39;main&#39;

Add response_format argument for OpenAI&#39;s models

See merge request deepsense.ai/g-internal/db-ally!40 ([`4bd176f`](https://github.com/deepsense-ai/db-ally/commit/4bd176ff872526a552c532b1b045f9c0923328cb))

* Add comment ([`c19b439`](https://github.com/deepsense-ai/db-ally/commit/c19b439b4f0b70737ce106594648915a1acca3d8))

* Add response_format argument for turbo models ([`53decb7`](https://github.com/deepsense-ai/db-ally/commit/53decb78c0f6922d5cf2bcbf4d6d197fbdb3f80f))

* Better IQL preprocessing ([`8393908`](https://github.com/deepsense-ai/db-ally/commit/8393908b56125e129b4f0a166e0001497cb3a585))

* Merge branch &#39;sc/fallback&#39; into &#39;main&#39;

Fallback

See merge request deepsense.ai/g-internal/db-ally!36 ([`21ba589`](https://github.com/deepsense-ai/db-ally/commit/21ba58961e534244400661fc2fdf9b54d4d0186e))

* add: Fallback mechanism ([`68ee750`](https://github.com/deepsense-ai/db-ally/commit/68ee750c5907c8815ecabf818eae3c360b9f3430))

* Merge branch &#39;mh/cast_types&#39; into &#39;main&#39;

Cast basic types in IQL functions

See merge request deepsense.ai/g-internal/db-ally!35 ([`7cd605b`](https://github.com/deepsense-ai/db-ally/commit/7cd605b1e1a25a735a4c74d505ac26ec444dae88))

* Merge branch &#39;mh/better_iql_generation_prompt&#39; into &#39;main&#39;

Better IQL example

See merge request deepsense.ai/g-internal/db-ally!37 ([`8568abd`](https://github.com/deepsense-ai/db-ally/commit/8568abd6fb6f7c7b391d468f0874fc5895380e4c))

* Better IQL example ([`b109fc6`](https://github.com/deepsense-ai/db-ally/commit/b109fc64c4339400cfd96400ef574762492c3afb))

* Change reasons in ValidationErrors ([`052ec9d`](https://github.com/deepsense-ai/db-ally/commit/052ec9d8508d83b851f552fb37eeb26e869cf159))

* Fix literal test ([`5d25d42`](https://github.com/deepsense-ai/db-ally/commit/5d25d42bba2f253ed468996c2dfd4406bc8a52e8))

* Cast basic types ([`8bbd0f4`](https://github.com/deepsense-ai/db-ally/commit/8bbd0f4a192570ae1012469f1445ee3a35a813b2))

* Merge branch &#39;pk/benchmark-adjustment&#39; into &#39;main&#39;

Benchmark calculate_exec_acc improvement, superhero example improvement

See merge request deepsense.ai/g-internal/db-ally!32 ([`a87743b`](https://github.com/deepsense-ai/db-ally/commit/a87743b66a37851bf157aa326422e80c40604cd1))

* Benchmark calculate_exec_acc improvement, superhero example improvement ([`c722104`](https://github.com/deepsense-ai/db-ally/commit/c72210403308f10ae7be263c9a4b1e616bea5e42))

* Merge branch &#39;sc/pretty-printing&#39; into &#39;main&#39;

Pretty printing

See merge request deepsense.ai/g-internal/db-ally!34 ([`4472a28`](https://github.com/deepsense-ai/db-ally/commit/4472a28c62948839e44e53843eb7887cb19ea377))

* Pretty printing ([`948216a`](https://github.com/deepsense-ai/db-ally/commit/948216abe851d739ef7cb5cf4ed559e478754c06))

* Merge branch &#39;mh/iql_validation&#39; into &#39;main&#39;

Validate IQL methods / arguments in IQLParser

See merge request deepsense.ai/g-internal/db-ally!33 ([`dec9a50`](https://github.com/deepsense-ai/db-ally/commit/dec9a507b6437112c7f510248d0ea201ec2857da))

* Merge branch &#39;ak/add-nl-responder&#39; into &#39;main&#39;

Add natural language reasoning component

See merge request deepsense.ai/g-internal/db-ally!26 ([`4ff6acd`](https://github.com/deepsense-ai/db-ally/commit/4ff6acd3b8aead49ccdf61f44d2829a68b8d0048))

* Merge branch &#39;main&#39; into ak/add-nl-responder ([`1a5bc86`](https://github.com/deepsense-ai/db-ally/commit/1a5bc860b043db3e5614921bce3e2cab09e36fd8))

* Limit rows and columns ([`cac7144`](https://github.com/deepsense-ai/db-ally/commit/cac7144f538a6df075525bf67781f31c990d93f9))

* Fix mypy ([`56667db`](https://github.com/deepsense-ai/db-ally/commit/56667dbb2bd0a91f8d2af4e1dc6b50d732abec64))

* Validate IQL methods / arguments in IQLParser ([`73fcd0b`](https://github.com/deepsense-ai/db-ally/commit/73fcd0b7ab92e91e2060f56eaf42e6968fecb315))

* Merge branch &#39;lt/collection_builder&#39; into &#39;main&#39;

Tests for using a collection with a view builder

See merge request deepsense.ai/g-internal/db-ally!31 ([`fa601cc`](https://github.com/deepsense-ai/db-ally/commit/fa601cc0e5f175ea2382510dacf741469a712182))

* Change prompt ([`d1597cb`](https://github.com/deepsense-ai/db-ally/commit/d1597cb5ba31077cc8b11bcd59a4b59e9e91bb86))

* Tests for using a collection with a view builder ([`5d39338`](https://github.com/deepsense-ai/db-ally/commit/5d39338400ed7277e4e7ca32a42aceedbb3909fe))

* Docstring improvement after comment ([`da9dbee`](https://github.com/deepsense-ai/db-ally/commit/da9dbee2d39dc243067b5ce43c9ce021162ed879))

* Remove redundant print ([`7d26241`](https://github.com/deepsense-ai/db-ally/commit/7d26241e6d3856aba771cb019ad91028219a8743))

* More changes ([`fb0fa4e`](https://github.com/deepsense-ai/db-ally/commit/fb0fa4e6424d895a0100d72934285a1c38ce8b5f))

* More changes after rebase ([`20ff30f`](https://github.com/deepsense-ai/db-ally/commit/20ff30f9725fc2ed42100fecc3960460da9cde25))

* Draft of changes after rebase ([`a6f390b`](https://github.com/deepsense-ai/db-ally/commit/a6f390b67ae5be34a536ad8cb2fbe9d5ebbbccba))

* Fix docstrings ([`cd831bc`](https://github.com/deepsense-ai/db-ally/commit/cd831bc683db1f732f7f6623115a04cf312bb250))

* Don&#39;t limit dataset ([`5e531be`](https://github.com/deepsense-ai/db-ally/commit/5e531be5196a04f37c9e786de2184c2cfb9ef37c))

* Fix mypy and benchmarks ([`95d2d79`](https://github.com/deepsense-ai/db-ally/commit/95d2d79b1fbdde699b818d797af72a8e7f4a3377))

* Add tests and fix requirements ([`c5de7b5`](https://github.com/deepsense-ai/db-ally/commit/c5de7b5117789130d3e6e96ea2a5ae8ab1b9b4ba))

* Include metadata in answer ([`641b3dc`](https://github.com/deepsense-ai/db-ally/commit/641b3dc96e13e64680b89a4a67a79b8a05e8c228))

* Small fix ([`f032e50`](https://github.com/deepsense-ai/db-ally/commit/f032e5007b1475ffaa4d1ca07d5836f8f960adc9))

* Add natural language reasoning component ([`9a35f8b`](https://github.com/deepsense-ai/db-ally/commit/9a35f8ba27691bbfd62281051d68799b31c31eee))

* Add initial changes in examples ([`57196b1`](https://github.com/deepsense-ai/db-ally/commit/57196b1c5dae98a079702e9747af02a61989ea50))

* Merge branch &#39;lt/execute&#39; into &#39;main&#39;

Better integrate view execution with the rest of the library

See merge request deepsense.ai/g-internal/db-ally!27 ([`1410df6`](https://github.com/deepsense-ai/db-ally/commit/1410df6fac8af1726ab405d254a4169cd8ab70f8))

* Better integrate view execution with the rest of the library ([`920a654`](https://github.com/deepsense-ai/db-ally/commit/920a65445200540f2a14eefdff163bdf861117a4))

* Merge branch &#39;lt/passing_view_parameters&#39; into &#39;main&#39;

Support for passing view-specific parameters

See merge request deepsense.ai/g-internal/db-ally!25 ([`9426327`](https://github.com/deepsense-ai/db-ally/commit/9426327fc73aae50f8b4abe7e5fdf399ad836b20))

* Support for passing view-specific parameters ([`459c69d`](https://github.com/deepsense-ai/db-ally/commit/459c69d368994aa58aa73107285857861f0e190b))

* Merge branch &#39;mh/langsmith_event_handler&#39; into &#39;main&#39;

Langsmith event handler

See merge request deepsense.ai/g-internal/db-ally!23 ([`abb915d`](https://github.com/deepsense-ai/db-ally/commit/abb915da2ba857559de87411d52fea09d48c33fc))

* Merge branch &#39;ak/add-dbally-benchmark&#39; into &#39;main&#39;

Integrate dbally with benchmark

See merge request deepsense.ai/g-internal/db-ally!20 ([`4c50194`](https://github.com/deepsense-ai/db-ally/commit/4c50194b4c9a62fe2e75db6813595e8762e13ab8))

* Add psycopg2 to whitelist ([`856d23f`](https://github.com/deepsense-ai/db-ally/commit/856d23f49abaf328df60b6f77ff4e8ef7665d2c3))

* Fix benchmark stage ([`11d0c5a`](https://github.com/deepsense-ai/db-ally/commit/11d0c5a8a6334858015e1cf22246361c9d957d00))

* Fix tests ([`6363a32`](https://github.com/deepsense-ai/db-ally/commit/6363a323ef9d38dd92ad4a59620a8e3065311a3a))

* Fix mypy ([`8873275`](https://github.com/deepsense-ai/db-ally/commit/8873275ee633c9edcef4cf9cc6157f2780bd7163))

* Set of fixes ([`9a248e5`](https://github.com/deepsense-ai/db-ally/commit/9a248e5f558c856fb8ad58fe85538b7ed4ee2647))

* Remove tokens from config ([`8ce941d`](https://github.com/deepsense-ai/db-ally/commit/8ce941d47f51dcd3f6b2b5a6a6a0015ebef1b08c))

* Add first version of benchmark ([`e35b4c6`](https://github.com/deepsense-ai/db-ally/commit/e35b4c60006f3af827db1fc6665f34b485763c00))

* Add tokens to LLMEvent ([`3404e46`](https://github.com/deepsense-ai/db-ally/commit/3404e46325b4382101d2cc87a5e786bdaa7d0db0))

* Add langsmith handler ([`4099889`](https://github.com/deepsense-ai/db-ally/commit/4099889a0a69e15e663acd12a887d4ec1d237a8b))

* Add collection_name to request start ([`da79170`](https://github.com/deepsense-ai/db-ally/commit/da79170f299a436ea8a93d64745fac86a29b3c17))

* Remove extra typing ([`9c59313`](https://github.com/deepsense-ai/db-ally/commit/9c5931305e0fe334e8a7a390137f60a0088bdac2))

* Use generics in event handlers ([`15821a4`](https://github.com/deepsense-ai/db-ally/commit/15821a46c77fad2724815f4e1ac781876e6a5b9c))

* Fix typings ([`f02f1e3`](https://github.com/deepsense-ai/db-ally/commit/f02f1e30e395ab83342172093442a348018115c7))

* Make event handlers stateless ([`cfdecab`](https://github.com/deepsense-ai/db-ally/commit/cfdecab2069fe9258331c284eae907b3ace91100))

* Merge branch &#39;ak/auditability-framework&#39; into &#39;main&#39;

Auditability framework

See merge request deepsense.ai/g-internal/db-ally!22 ([`061fe2c`](https://github.com/deepsense-ai/db-ally/commit/061fe2c30500c13dfb5eda413612b45e04725e51))

* Fix mypy ([`5e84749`](https://github.com/deepsense-ai/db-ally/commit/5e847497b81e75242e672bc891d7ea216d3d9dfa))

* fix pylint ([`c8a57af`](https://github.com/deepsense-ai/db-ally/commit/c8a57af7d7fca13d8bff705c3459317737e81a5b))

* Make rich optional in cli event handler ([`e146b2a`](https://github.com/deepsense-ai/db-ally/commit/e146b2a0a0042bd98e5f0250b246f8f629097a1e))

* EventStore -&gt; EventTracker ([`53afc11`](https://github.com/deepsense-ai/db-ally/commit/53afc116ab56ff137fd25781af0c4e551b2c2c8a))

* Fix mypy ([`350a5b6`](https://github.com/deepsense-ai/db-ally/commit/350a5b6ad4f877cf05e43e2a0145ec4fba538187))

* Fix mypy again ([`7b67a09`](https://github.com/deepsense-ai/db-ally/commit/7b67a093d24f6a5692d8eebbe91eb991f3d1f988))

* Fix mypy ([`66e52d3`](https://github.com/deepsense-ai/db-ally/commit/66e52d3c989b1a3849f3db53b0c1935c6cae7e50))

* Fix lint again ([`0c37784`](https://github.com/deepsense-ai/db-ally/commit/0c37784ee253f97d89d0dda979785354b5c6f4b0))

* Upgrade CLI output and fix lint ([`3d6d5b3`](https://github.com/deepsense-ai/db-ally/commit/3d6d5b3ab45153dcbda065fb7254df19cccd90e1))

* WIP: auditability framework ([`ddcc691`](https://github.com/deepsense-ai/db-ally/commit/ddcc691ba8f017d02c68589b8dac9653dbe6fc23))

* Add a draft of audit ([`b9a0780`](https://github.com/deepsense-ai/db-ally/commit/b9a0780f87a2fb9dbf0f97acb58110f6f84c51e6))

* Merge branch &#39;ak/benchmark-in-cicd&#39; into &#39;main&#39;

Benchmark in CI/CD

See merge request deepsense.ai/g-internal/db-ally!19 ([`854fb6e`](https://github.com/deepsense-ai/db-ally/commit/854fb6e0cd5b36642a4d2ad6049df604b042e9e2))

* Fix mypy ([`288a00d`](https://github.com/deepsense-ai/db-ally/commit/288a00d323197f295f37dba450d1f06d9686b5c8))

* Fix tests ([`d33764f`](https://github.com/deepsense-ai/db-ally/commit/d33764f24612e861394cbb81db2650a5d6bc99bc))

* Fix dockerfile ([`11376fb`](https://github.com/deepsense-ai/db-ally/commit/11376fba4b275fbe7f5e43f04f7198907885c01a))

* Fix dockerfile ([`c09082c`](https://github.com/deepsense-ai/db-ally/commit/c09082c56f3ae360cfbdc9e3c29d10f6578b1ed4))

* Small fix ([`3f1ad7f`](https://github.com/deepsense-ai/db-ally/commit/3f1ad7f33a17d7d24d4cfd412ed23ea9ed0c1181))

* Small change in deploy stage ([`20f28e7`](https://github.com/deepsense-ai/db-ally/commit/20f28e79048f04ca638eb0f85f30aa87383eeb97))

* Small change in deploy stage ([`171e8d8`](https://github.com/deepsense-ai/db-ally/commit/171e8d8d1a79834f12f9467a868b64cb21589c1b))

* Fixes after review ([`356501d`](https://github.com/deepsense-ai/db-ally/commit/356501d7ff65ce69bdf0a3c66e38e81d4f71aaec))

* Remove dataset limit ([`fd76e81`](https://github.com/deepsense-ai/db-ally/commit/fd76e812a30297fc0937e4b59356b5d62f24bb03))

* Fix dockerfile ([`14a5b4e`](https://github.com/deepsense-ai/db-ally/commit/14a5b4ee7449b73c3e982fa12930d6bf0ee25235))

* Change experiment config ([`7be1489`](https://github.com/deepsense-ai/db-ally/commit/7be1489bf81e3b07de494dbed6115fefb0f8cdb6))

* Fix pydantic version ([`68be902`](https://github.com/deepsense-ai/db-ally/commit/68be902a6ea8688d074208761ebc3e8d2c594bed))

* Limit dataset to debug ([`7ac03b9`](https://github.com/deepsense-ai/db-ally/commit/7ac03b99351d0ddda8b7d74dc216d55002276df4))

* Replace todo with script ([`1c5756e`](https://github.com/deepsense-ai/db-ally/commit/1c5756ed3c44b152d59d4c008c9a9f2c7766b318))

* Add benchmark to CI/CD ([`b53d35a`](https://github.com/deepsense-ai/db-ally/commit/b53d35af5ac98e3ae22079422dcd5ae8a7dd45de))

* Merge branch &#39;pk/view-selector&#39; into &#39;main&#39;

View selection

See merge request deepsense.ai/g-internal/db-ally!17 ([`e82801b`](https://github.com/deepsense-ai/db-ally/commit/e82801bef24af38fd9f650ffe69d192201291154))

* Fix tests (openai missing) ([`f927075`](https://github.com/deepsense-ai/db-ally/commit/f927075cd3b333401c3fa94592894604d8ecf4a1))

* Merge branch &#39;mh/add_retail_shop&#39; into &#39;main&#39;

Add clothes retail database

See merge request deepsense.ai/g-internal/db-ally!18 ([`4b58f3d`](https://github.com/deepsense-ai/db-ally/commit/4b58f3d2aac9dadb845ab4f61084d69b7af84fa6))

* Add clothes retail database ([`efa7612`](https://github.com/deepsense-ai/db-ally/commit/efa76120750b0dea484f19ff9940131b763a3bc6))

* Fix test ([`36abc94`](https://github.com/deepsense-ai/db-ally/commit/36abc94a21e8c8e8996c0059fde0384900b6b997))

* Integrate IQL generator and view selector with a pipeline ([`a5ab9b1`](https://github.com/deepsense-ai/db-ally/commit/a5ab9b15372533fd5d30bd8c97f809b0fa3ebc40))

* unit test ([`2bbd8d8`](https://github.com/deepsense-ai/db-ally/commit/2bbd8d88f8bd9c7a518df8ff2705be55b4a3f551))

* DefaultViewSelector implementation ([`4238dcf`](https://github.com/deepsense-ai/db-ally/commit/4238dcf8505d2148a2340fb2ca046eee3a7a949d))

* superhero view2 tweak ([`388cb45`](https://github.com/deepsense-ai/db-ally/commit/388cb4583e2c54b23ebf5d80938395ff69e1df2a))

* add another view to superhero example ([`2ee15e4`](https://github.com/deepsense-ai/db-ally/commit/2ee15e42df1389bfd235d4d8afd066e26b09c49b))

* adjust iql generator to return filters and actions separately, like expected in collections ([`2c65ab1`](https://github.com/deepsense-ai/db-ally/commit/2c65ab1ace99bbb120fef53684a3af76c7990f2f))

* Merge branch &#39;ak/implement-llm-client&#39; into &#39;main&#39;

Implement OpenAI API client

See merge request deepsense.ai/g-internal/db-ally!14 ([`3e78269`](https://github.com/deepsense-ai/db-ally/commit/3e78269214c59c9160cb552c69896517d61f20b7))

* Add LLM client

Add missing init file

Fix mypy

Fix lint again

Fixes after review

Fix lint

Fixes after rebasing

Fix lint

Fix mypy

Small fix ([`9f3fad4`](https://github.com/deepsense-ai/db-ally/commit/9f3fad4a73dcd5012cb8beef1bcb1953c12cff92))

* Merge branch &#39;pk/iql-generator-mypy-fix&#39; into &#39;main&#39;

IQLGenerator tests - add ignoring mypy

See merge request deepsense.ai/g-internal/db-ally!16 ([`3e1f7ed`](https://github.com/deepsense-ai/db-ally/commit/3e1f7ed8e2cc721bb313289e9b4f073732bc2ef3))

* ignore mypy ([`51aa497`](https://github.com/deepsense-ai/db-ally/commit/51aa49710334158fe7ae3bb8cff2bef4f600dc10))

* Merge branch &#39;pk/llm-iql-generation&#39; into &#39;main&#39;

IQLGenerator

See merge request deepsense.ai/g-internal/db-ally!11 ([`fd99707`](https://github.com/deepsense-ai/db-ally/commit/fd9970784f868a2272f7759c8f375e127176665f))

* IQLGenerator
added llm_output_parser and output_format to PromptTemplate
IQLPromptTemplate ([`fbd9bfe`](https://github.com/deepsense-ai/db-ally/commit/fbd9bfeeb3ecca06c52f49f8e5cf999962c8153a))

* Merge branch &#39;lt/remove_registry&#39; into &#39;main&#39;

Remove view registry (replace with collection)

See merge request deepsense.ai/g-internal/db-ally!15 ([`06367cd`](https://github.com/deepsense-ai/db-ally/commit/06367cddfa2cc6d82e04e33e61c03b76abc26051))

* Remove view registry (replace with collection) ([`0b15cf0`](https://github.com/deepsense-ai/db-ally/commit/0b15cf00be3a6274a78718eae538a9387343205e))

* Merge branch &#39;mh/add_collections&#39; into &#39;main&#39;

Add collections / initial question answering flow

See merge request deepsense.ai/g-internal/db-ally!12 ([`b5a010e`](https://github.com/deepsense-ai/db-ally/commit/b5a010e75c90dc7e5700708a90c908ee79f8fe5f))

* Add sql execution to example ([`bc663b3`](https://github.com/deepsense-ai/db-ally/commit/bc663b375e867c81d78fe56f19ecd31248e69f0d))

* Rename DBAllyCollection -&gt; Collection ([`841c114`](https://github.com/deepsense-ai/db-ally/commit/841c114ef31078b507ffad583918fde7520d0465))

* Merge branch &#39;lt/mypy_tests&#39; into &#39;main&#39;

Add mypy type checking to tests

See merge request deepsense.ai/g-internal/db-ally!13 ([`549c896`](https://github.com/deepsense-ai/db-ally/commit/549c896fe7eaa0c95f3fe185a66dd7d3cc0bb924))

* Fix errors in typing definitions ([`f698234`](https://github.com/deepsense-ai/db-ally/commit/f6982346f902e37da7f08e31505affa018a21ae6))

* Add mypy type checking to tests ([`5c68959`](https://github.com/deepsense-ai/db-ally/commit/5c689593d60d6324be2c74c1c91ae8fa4649628f))

* Add collections / initial question answering flow ([`6698e31`](https://github.com/deepsense-ai/db-ally/commit/6698e314cc611800deab18a2e93a7e731c1b7bae))

* Merge branch &#39;mh/integrate_query_parsing_with_query_building&#39; into &#39;main&#39;

Integrate query parsing with query building

See merge request deepsense.ai/g-internal/db-ally!10 ([`3691758`](https://github.com/deepsense-ai/db-ally/commit/3691758c168b9fe99588841ae8f40d3ea331eeb8))

* Merge branch &#39;pk/superhero-example&#39; into &#39;main&#39;

Add superhero example

See merge request deepsense.ai/g-internal/db-ally!5 ([`079d1a3`](https://github.com/deepsense-ai/db-ally/commit/079d1a38e3b9f963de3c9d1daecc979df6d29009))

* Add superhero example ([`c03b500`](https://github.com/deepsense-ai/db-ally/commit/c03b5005f550f6e74f94d62990368bf3924d3175))

* Fix tests ([`0a74e51`](https://github.com/deepsense-ai/db-ally/commit/0a74e51d6d0e2463b4a9c896a2af059f826b13f2))

* Integrate query parsing with query building ([`8728327`](https://github.com/deepsense-ai/db-ally/commit/872832722e58d504edc6e438f2e1f2aba6080f70))

* Move iql test ([`04e57e6`](https://github.com/deepsense-ai/db-ally/commit/04e57e60878e9e289d81a8101aed37f57fa2e8f3))

* Merge branch &#39;ak/text2sql-benchmark&#39; into &#39;main&#39;

Text2SQL benchmark

See merge request deepsense.ai/g-internal/db-ally!6 ([`44f19de`](https://github.com/deepsense-ai/db-ally/commit/44f19de252a47f8d97f18b574e9e2fe551217085))

* Small fix ([`0387b6e`](https://github.com/deepsense-ai/db-ally/commit/0387b6e3c3761e970b457af8773cdf1c9fd0ac84))

* Move io.py and paths.py files ([`530d5cd`](https://github.com/deepsense-ai/db-ally/commit/530d5cdf8852bcc3995fb371dcfdcce6e335811f))

* Use PromptBuilder ([`9300eaa`](https://github.com/deepsense-ai/db-ally/commit/9300eaa79f52caf1ab01b0d069a30affa733eab2))

* Integrate config and move prompt templates ([`a59ac9d`](https://github.com/deepsense-ai/db-ally/commit/a59ac9d84ae9df4a8493c1023647f7fa49418519))

* Add missing file ([`eaf170c`](https://github.com/deepsense-ai/db-ally/commit/eaf170c36cde97efeefcbc02bb48e47e2fbf43d0))

* Fixes after review ([`b9cd679`](https://github.com/deepsense-ai/db-ally/commit/b9cd679903a193bfb2bfad86a582054d5843ee13))

* Fix lint ([`006690d`](https://github.com/deepsense-ai/db-ally/commit/006690d51e422c2efe269e942946a93b6ea88f1a))

* Fix bug ([`4d043db`](https://github.com/deepsense-ai/db-ally/commit/4d043dbb8d1536b6830ab016e1cd75a7fc1e6c3b))

* Add open.ai support ([`a590833`](https://github.com/deepsense-ai/db-ally/commit/a590833cad785b30dd0da2f872c0220769f7a987))

* Add evaluation script ([`4ff14b0`](https://github.com/deepsense-ai/db-ally/commit/4ff14b075567a4e878c425a64566b9c1d1e852f5))

* Merge branch &#39;lt/views_tests&#39; into &#39;main&#39;

Basic tests for views

See merge request deepsense.ai/g-internal/db-ally!9 ([`7fab89f`](https://github.com/deepsense-ai/db-ally/commit/7fab89fed0b0d3ff68f44c2e391e92b674de5c3a))

* Basic tests for views ([`e9e1a24`](https://github.com/deepsense-ai/db-ally/commit/e9e1a24b5ab79affbbd94839fcf1dedd67216277))

* Merge branch &#39;pk/prompt-builder&#39; into &#39;main&#39;

Add PromptBuilder, PromptTemplate, tests

See merge request deepsense.ai/g-internal/db-ally!8 ([`f23d340`](https://github.com/deepsense-ai/db-ally/commit/f23d3401e4748bb8f2b9505d41f57b4835218530))

* Add PromptBuilder, PromptTemplate, tests ([`4a2a781`](https://github.com/deepsense-ai/db-ally/commit/4a2a78124819ed18ef80a61f3f1642c49de50f94))

* Merge branch &#39;lt/views&#39; into &#39;main&#39;

Introduce view-based SQL generation

See merge request deepsense.ai/g-internal/db-ally!4 ([`9785574`](https://github.com/deepsense-ai/db-ally/commit/97855745484b83a20bf8d8001e520feaa7bf1092))

* Introduce view-based SQL generation ([`784876b`](https://github.com/deepsense-ai/db-ally/commit/784876b955c4592bd86e3959c3cd7fee0d8cdb56))

* Merge branch &#39;DBALL-7-handle-iql-parsing&#39; into &#39;main&#39;

Initial IQL definition and parsing

See merge request deepsense.ai/g-internal/db-ally!7 ([`b6be39e`](https://github.com/deepsense-ai/db-ally/commit/b6be39e2ee8d94c531865e8b3f72714ba467d1d7))

* Remove IQL namespace; make syntax module public ([`0ccc374`](https://github.com/deepsense-ai/db-ally/commit/0ccc3741950f9e71ac3b69a285c6983ea800009b))

* Apply lint rules ([`0a22aba`](https://github.com/deepsense-ai/db-ally/commit/0a22abab30819e5f98cfd7c56fe8a571accfa65e))

* Add unit tests for IQL module ([`b2ef1a8`](https://github.com/deepsense-ai/db-ally/commit/b2ef1a82081b3859330c3184adeacb25e295a4b1))

* IQL module index ([`a979c0b`](https://github.com/deepsense-ai/db-ally/commit/a979c0b9eebac6994c74cd505c012a999e976526))

* Add IQLQuery container class ([`b3bbe55`](https://github.com/deepsense-ai/db-ally/commit/b3bbe552ae714c374bcf0b3aea195962cc453c7e))

* Implement IQLParser ([`ce1c6b9`](https://github.com/deepsense-ai/db-ally/commit/ce1c6b967e1ddadaf28d84d47cd92ceb5a33e111))

* Define IQL Syntax elements ([`748dde0`](https://github.com/deepsense-ai/db-ally/commit/748dde02fab28c10aba6589c8002bee4bb11bc0f))

* Merge branch &#39;fk/terraform-database-setup&#39; into &#39;main&#39;

Terraform GCP databases setup

See merge request deepsense.ai/g-internal/db-ally!2 ([`adb815a`](https://github.com/deepsense-ai/db-ally/commit/adb815a3173ade9143fda077271d55ab1074dc8f))

* Terraform GCP databases setup ([`2c262eb`](https://github.com/deepsense-ai/db-ally/commit/2c262ebf7c5496f22ae6e81c8ccbb5138154befc))

* Merge branch &#39;pk/python-version&#39; into &#39;main&#39;

python version 3.8

See merge request deepsense.ai/g-internal/db-ally!3 ([`33a11da`](https://github.com/deepsense-ai/db-ally/commit/33a11da15138c3df7aeee4811584fea471de229d))

* set runner image to python:3-8 ([`102c6b0`](https://github.com/deepsense-ai/db-ally/commit/102c6b0e6faa84e6d0bd00ac9c74cf9a25ef395e))

* add python version 3.8 ([`754e38b`](https://github.com/deepsense-ai/db-ally/commit/754e38ba0f08adae344753d52efb3f2c7be41c62))

* Merge branch &#39;mh/template&#39; into &#39;main&#39;

Setup ds-template

See merge request deepsense.ai/g-internal/db-ally!1 ([`561a0c6`](https://github.com/deepsense-ai/db-ally/commit/561a0c64531252f9e4f05f108035f74f24b711b6))

* Merge branch &#39;main&#39; into &#39;mh/template&#39; ([`caf7cdc`](https://github.com/deepsense-ai/db-ally/commit/caf7cdc6488d25b07a4d1e41dcb03dcb89c63665))

* Setup ds-template ([`665a25f`](https://github.com/deepsense-ai/db-ally/commit/665a25f8536b8df57a9edc4addaff535c7da5f69))

* Initial commit ([`629c656`](https://github.com/deepsense-ai/db-ally/commit/629c6567c8f7cd21f3b18643b14f9c697037739e))
