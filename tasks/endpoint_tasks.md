# Follow Up Boss API Endpoints

## Events
- [x] GET /v1/events (List events)
- [x] POST /v1/events (Create event)
- [ ] GET /v1/events/{id} (Retrieve event)

## People
- [x] GET /v1/people (List people)
- [x] POST /v1/people (Create person)
- [x] GET /v1/people/{id} (Retrieve person)
- [x] PUT /v1/people/{id} (Update person)
- [x] DELETE /v1/people/{id} (Delete person)
- [x] GET /v1/people/checkDuplicate (Check for duplicate people)
- [x] GET /v1/people/unclaimed (List unclaimed people)
- [ ] POST /v1/people/claim (Claim an unclaimed person)
- [ ] POST /v1/people/ignoreUnclaimed (Ignore an unclaimed person)

## Person Attachments
- [ ] POST /v1/personAttachments (Add attachment to person) # BLOCKED: API Key Permissions (Confirmed 403 Forbidden: "You do not have access to this API endpoint.")
- [ ] GET /v1/personAttachments/{id} (Retrieve person attachment) # BLOCKED: Prerequisite (POST) fails due to API Key Permissions.
- [ ] PUT /v1/personAttachments/{id} (Update person attachment) # BLOCKED: Prerequisite (POST) fails due to API Key Permissions.
- [ ] DELETE /v1/personAttachments/{id} (Delete person attachment) # BLOCKED: Prerequisite (POST) fails due to API Key Permissions.

## People Relationships
- [ ] GET /v1/peopleRelationships (List people relationships) # Tested: Works (returns empty list on test account).
- [ ] POST /v1/peopleRelationships (Create people relationship) # BLOCKED: Payload structure unconfirmed; API returns 400 "Invalid fields in the request body: X" where X has included relatedPersonId, relatedId, person2Id, contactId, relatedPerson object. `personId` and `type` fields seem to be accepted.
- [ ] GET /v1/peopleRelationships/{id} (Retrieve people relationship) # BLOCKED: Prerequisite (POST) fails.
- [ ] PUT /v1/peopleRelationships/{id} (Update people relationship) # BLOCKED: Prerequisite (POST) fails.
- [ ] DELETE /v1/peopleRelationships/{id} (Delete people relationship) # BLOCKED: Prerequisite (POST) fails.

## Identity
- [x] GET /v1/identity (Get identity information)

## Notes
- [x] GET /v1/notes (List notes)
- [x] POST /v1/notes (Create note)
- [x] GET /v1/notes/{id} (Retrieve note)
- [x] PUT /v1/notes/{id} (Update note)
- [x] DELETE /v1/notes/{id} (Delete note)

## Calls
- [x] GET /v1/calls (List calls)
- [x] POST /v1/calls (Create call)
- [x] GET /v1/calls/{id} (Retrieve call)
- [x] PUT /v1/calls/{id} (Update call)

## Text Messages
- [ ] GET /v1/textMessages (List text messages)
- [ ] POST /v1/textMessages (Create text message)
- [ ] GET /v1/textMessages/{id} (Retrieve text message)

## Users
- [x] GET /v1/users (List users)
- [x] GET /v1/users/{id} (Retrieve user)
- [ ] DELETE /v1/users/{id} (Delete user) # Implemented, not auto-tested due to sensitivity
- [x] GET /v1/me (Get current user)

## Smart Lists
- [ ] GET /v1/smartLists (List Smart Lists)
- [ ] GET /v1/smartLists/{id} (Retrieve Smart List)

## Action Plans
- [ ] GET /v1/actionPlans (List action plans)
- [ ] GET /v1/actionPlansPeople (List people in action plans)
- [ ] POST /v1/actionPlansPeople (Add person to action plan)
- [ ] PUT /v1/actionPlansPeople/{id} (Update person in action plan)

## Email Templates
- [ ] GET /v1/templates (List email templates)
- [ ] POST /v1/templates (Create email template)
- [ ] GET /v1/templates/{id} (Retrieve email template)
- [ ] PUT /v1/templates/{id} (Update email template)
- [ ] POST /v1/templates/merge (Merge email template)
- [ ] DELETE /v1/templates/{id} (Delete email template)

## Text Message Templates
- [ ] GET /v1/textMessageTemplates (List text message templates)
- [ ] POST /v1/textMessageTemplates (Create text message template)
- [ ] GET /v1/textMessageTemplates/{id} (Retrieve text message template)
- [ ] PUT /v1/textMessageTemplates/{id} (Update text message template)
- [ ] POST /v1/textMessageTemplates/merge (Merge text message template)
- [ ] DELETE /v1/textMessageTemplates/{id} (Delete text message template)

## Email Marketing
- [ ] GET /v1/emEvents (List email marketing events)
- [ ] POST /v1/emEvents (Create email marketing event)
- [ ] GET /v1/emCampaigns (List email marketing campaigns)
- [ ] POST /v1/emCampaigns (Create email marketing campaign)
- [ ] PUT /v1/emCampaigns/{id} (Update email marketing campaign)

## Custom Fields
- [ ] GET /v1/customFields (List custom fields)
- [ ] POST /v1/customFields (Create custom field)
- [ ] GET /v1/customFields/{id} (Retrieve custom field)
- [ ] PUT /v1/customFields/{id} (Update custom field)
- [ ] DELETE /v1/customFields/{id} (Delete custom field)

## Stages
- [ ] GET /v1/stages (List stages)
- [ ] POST /v1/stages (Create stage) # Tested: Accepts pipelineId in payload with X-System headers, but created stage may not be correctly recognized by Deal creation.
- [ ] GET /v1/stages/{id} (Retrieve stage)
- [ ] PUT /v1/stages/{id} (Update stage)
- [ ] DELETE /v1/stages/{id} (Delete stage) # BLOCKED: Requires `assignStageId` in payload, not yet implemented in test/wrapper.

## Tasks
- [ ] GET /v1/tasks (List tasks)
- [ ] POST /v1/tasks (Create task)
- [ ] GET /v1/tasks/{id} (Retrieve task)
- [ ] PUT /v1/tasks/{id} (Update task)
- [ ] DELETE /v1/tasks/{id} (Delete task)

## Appointments
- [ ] GET /v1/appointments (List appointments)
- [ ] POST /v1/appointments (Create appointment) # BLOCKED - API returns 400 "Valid Start and End dates are required" when startTime, endTime, appointmentTypeId are query params. Body seems to expect title, description, location, invitees.
- [ ] GET /v1/appointments/{id} (Retrieve appointment) # BLOCKED - Prerequisite (POST) fails.
- [ ] PUT /v1/appointments/{id} (Update appointment) # BLOCKED - Prerequisite (POST) fails.
- [ ] DELETE /v1/appointments/{id} (Delete appointment) # BLOCKED - Prerequisite (POST) fails.

## Appointment Types
- [ ] GET /v1/appointmentTypes (List appointment types)
- [ ] POST /v1/appointmentTypes (Create appointment type)
- [ ] GET /v1/appointmentTypes/{id} (Retrieve appointment type)
- [ ] PUT /v1/appointmentTypes/{id} (Update appointment type)
- [ ] DELETE /v1/appointmentTypes/{id} (Delete appointment type)

## Appointment Outcomes
- [ ] GET /v1/appointmentOutcomes (List appointment outcomes)
- [ ] POST /v1/appointmentOutcomes (Create appointment outcome)
- [ ] GET /v1/appointmentOutcomes/{id} (Retrieve appointment outcome)
- [ ] PUT /v1/appointmentOutcomes/{id} (Update appointment outcome)
- [ ] DELETE /v1/appointmentOutcomes/{id} (Delete appointment outcome)

## Webhooks
- [ ] GET /v1/webhooks (List webhooks)
- [ ] POST /v1/webhooks (Create webhook)
- [ ] GET /v1/webhooks/{id} (Retrieve webhook)
- [ ] PUT /v1/webhooks/{id} (Update webhook)
- [ ] DELETE /v1/webhooks/{id} (Delete webhook)

## Webhook Events
- [ ] GET /v1/webhookEvents/{id} (Retrieve webhook event) # Tested: Wrapper works (404 for dummy ID as expected).

## Pipelines
- [ ] GET /v1/pipelines (List pipelines)
- [ ] POST /v1/pipelines (Create pipeline) # Tested: Works.
- [ ] GET /v1/pipelines/{id} (Retrieve pipeline)
- [ ] PUT /v1/pipelines/{id} (Update pipeline)
- [ ] DELETE /v1/pipelines/{id} (Delete pipeline)

## Deals
- [ ] GET /v1/deals (List deals)
- [ ] POST /v1/deals (Create deal) # INVESTIGATE: Blocked - Fails with 400 "stage not found, or not a pipeline stage" even when stage is created in pipeline. Contact association (contacts: [{"id":id}]) also needs full test.
- [ ] GET /v1/deals/{id} (Retrieve deal)
- [ ] PUT /v1/deals/{id} (Update deal)
- [ ] DELETE /v1/deals/{id} (Delete deal)

## Deal Attachments
- [ ] POST /v1/dealAttachments (Add attachment to deal) # BLOCKED: Prerequisite (Deal creation) fails.
- [ ] GET /v1/dealAttachments/{id} (Retrieve deal attachment) # BLOCKED: Prerequisite (Deal creation) fails.
- [ ] PUT /v1/dealAttachments/{id} (Update deal attachment) # BLOCKED: Prerequisite (Deal creation) fails.
- [ ] DELETE /v1/dealAttachments/{id} (Delete deal attachment) # BLOCKED: Prerequisite (Deal creation) fails.

## Deals Custom Fields
- [ ] GET /v1/dealCustomFields (List deal custom fields)
- [ ] POST /v1/dealCustomFields (Create deal custom field)
- [ ] GET /v1/dealCustomFields/{id} (Retrieve deal custom field)
- [ ] PUT /v1/dealCustomFields/{id} (Update deal custom field)
- [ ] DELETE /v1/dealCustomFields/{id} (Delete deal custom field)

## Groups
- [ ] GET /v1/groups (List groups)
- [ ] GET /v1/groups/roundRobin (Get group round robin status)
- [ ] POST /v1/groups (Create group)
- [ ] GET /v1/groups/{id} (Retrieve group)
- [ ] PUT /v1/groups/{id} (Update group)
- [ ] DELETE /v1/groups/{id} (Delete group)

## Teams
- [ ] GET /v1/teams (List teams)
- [ ] POST /v1/teams (Create team)
- [ ] GET /v1/teams/{id} (Retrieve team)
- [ ] PUT /v1/teams/{id} (Update team)
- [ ] DELETE /v1/teams/{id} (Delete team)

## Team Inboxes
- [ ] GET /v1/teamInboxes (List team inboxes)

## Ponds
- [ ] GET /v1/ponds (List ponds)
- [ ] POST /v1/ponds (Create pond)
- [ ] GET /v1/ponds/{id} (Retrieve pond)
- [ ] PUT /v1/ponds/{id} (Update pond)
- [ ] DELETE /v1/ponds/{id} (Delete pond)

## Inbox Apps
- [ ] POST /v1/inboxApps/install (Install inbox app) # BLOCKED: Requires X-System-Key header (now provided), but API returns 400 "publishedInboxAppId is required."
- [ ] POST /v1/inboxApps/addMessage (Add message to inbox app) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.
- [ ] PUT /v1/inboxApps/updateMessage (Update message in inbox app) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.
- [ ] POST /v1/inboxApps/addNote (Add note to inbox app conversation) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.
- [ ] PUT /v1/inboxApps/updateConversation (Update inbox app conversation) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.
- [ ] GET /v1/inboxApps/getParticipants (Get participants of inbox app conversation) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.
- [ ] POST /v1/inboxApps/addParticipant (Add participant to inbox app conversation) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.
- [ ] DELETE /v1/inboxApps/removeParticipant (Remove participant from inbox app conversation) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.
- [ ] DELETE /v1/inboxApps/deactivate (Deactivate inbox app) # BLOCKED: Prerequisite (install) requires valid publishedInboxAppId.

## Reactions
- [ ] POST /v1/reactions/{refType}/{refId} (Create reaction) # Tested: Works (returns [], payload {"body": emoji}).
- [ ] GET /v1/reactions/{id} (Retrieve reaction) # Tested: Works. ID discoverable via GET /notes/{id}?includeReactions=true.
- [ ] DELETE /v1/reactions/{refType}/{refId} (Delete reaction) # Tested: Works (payload {"body": emoji}, not {"emoji": emoji}).

## Threaded Replies
- [ ] GET /v1/threadedReplies/{id} (Retrieve threaded reply) # Tested: Wrapper works (404 for dummy ID as expected).

## Timeframes
- [ ] GET /v1/timeframes (List timeframes) 