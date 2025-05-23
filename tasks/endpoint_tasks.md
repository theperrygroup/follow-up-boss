# Follow Up Boss API Endpoints

## Events
- [x] GET /v1/events (List events)
- [x] POST /v1/events (Create event)
- [x] GET /v1/events/{id} (Retrieve event)

## People
- [x] GET /v1/people (List people)
- [x] POST /v1/people (Create person)
- [x] GET /v1/people/{id} (Retrieve person)
- [x] PUT /v1/people/{id} (Update person)
- [x] DELETE /v1/people/{id} (Delete person)
- [x] GET /v1/people/checkDuplicate (Check for duplicate people)
- [x] GET /v1/people/unclaimed (List unclaimed people)
- [x] POST /v1/people/claim (Claim an unclaimed person)
- [x] POST /v1/people/ignoreUnclaimed (Ignore an unclaimed person)

## Person Attachments
- [ ] POST /v1/personAttachments (Add attachment to person) # TODO: Needs specific API documentation for file upload format
- [ ] GET /v1/personAttachments/{id} (Retrieve person attachment) # TODO: Needs specific API documentation
- [ ] PUT /v1/personAttachments/{id} (Update person attachment) # TODO: Needs specific API documentation
- [ ] DELETE /v1/personAttachments/{id} (Delete person attachment) # TODO: Needs specific API documentation

## People Relationships
- [x] GET /v1/peopleRelationships (List people relationships) # Tested: Works (returns empty list on test account).
- [x] POST /v1/peopleRelationships (Create people relationship) # NOTE: API expects only `personId` and `type`, doesn't accept related person ID fields.
- [x] GET /v1/peopleRelationships/{id} (Retrieve people relationship)
- [x] PUT /v1/peopleRelationships/{id} (Update people relationship)
- [x] DELETE /v1/peopleRelationships/{id} (Delete people relationship)

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
- [x] GET /v1/textMessages (List text messages)
- [x] POST /v1/textMessages (Create text message)
- [x] GET /v1/textMessages/{id} (Retrieve text message)

## Users
- [x] GET /v1/users (List users)
- [x] GET /v1/users/{id} (Retrieve user)
- [x] DELETE /v1/users/{id} (Delete user) # Implemented, not auto-tested due to sensitivity
- [x] GET /v1/me (Get current user)

## Smart Lists
- [x] GET /v1/smartLists (List Smart Lists)
- [x] GET /v1/smartLists/{id} (Retrieve Smart List)

## Action Plans
- [x] GET /v1/actionPlans (List action plans)
- [x] GET /v1/actionPlansPeople (List people in action plans)
- [x] POST /v1/actionPlansPeople (Add person to action plan)
- [x] PUT /v1/actionPlansPeople/{id} (Update person in action plan)

## Email Templates
- [x] GET /v1/templates (List email templates)
- [x] POST /v1/templates (Create email template)
- [x] GET /v1/templates/{id} (Retrieve email template)
- [x] PUT /v1/templates/{id} (Update email template)
- [x] POST /v1/templates/merge (Merge email template)
- [x] DELETE /v1/templates/{id} (Delete email template)

## Text Message Templates
- [x] GET /v1/textMessageTemplates (List text message templates)
- [x] POST /v1/textMessageTemplates (Create text message template)
- [x] GET /v1/textMessageTemplates/{id} (Retrieve text message template)
- [x] PUT /v1/textMessageTemplates/{id} (Update text message template)
- [x] POST /v1/textMessageTemplates/merge (Merge text message template)
- [x] DELETE /v1/textMessageTemplates/{id} (Delete text message template)

## Email Marketing
- [x] GET /v1/emEvents (List email marketing events)
- [x] POST /v1/emEvents (Create email marketing event)
- [x] GET /v1/emCampaigns (List email marketing campaigns)
- [x] POST /v1/emCampaigns (Create email marketing campaign)
- [x] PUT /v1/emCampaigns/{id} (Update email marketing campaign)

## Custom Fields
- [x] GET /v1/customFields (List custom fields)
- [x] POST /v1/customFields (Create custom field)
- [x] GET /v1/customFields/{id} (Retrieve custom field)
- [x] PUT /v1/customFields/{id} (Update custom field)
- [x] DELETE /v1/customFields/{id} (Delete custom field) # NOTE: Not tested to avoid removing existing fields

## Stages
- [x] GET /v1/stages (List stages)
- [x] POST /v1/stages (Create stage)
- [x] GET /v1/stages/{id} (Retrieve stage)
- [x] PUT /v1/stages/{id} (Update stage)
- [x] DELETE /v1/stages/{id} (Delete stage)

## Tasks
- [x] GET /v1/tasks (List tasks)
- [x] POST /v1/tasks (Create task)
- [x] GET /v1/tasks/{id} (Retrieve task)
- [x] PUT /v1/tasks/{id} (Update task)
- [x] DELETE /v1/tasks/{id} (Delete task)

## Appointments
- [x] GET /v1/appointments (List appointments)
- [x] POST /v1/appointments (Create appointment)
- [x] GET /v1/appointments/{id} (Retrieve appointment)
- [x] PUT /v1/appointments/{id} (Update appointment)
- [x] DELETE /v1/appointments/{id} (Delete appointment)

## Appointment Types
- [x] GET /v1/appointmentTypes (List appointment types)
- [x] POST /v1/appointmentTypes (Create appointment type)
- [x] GET /v1/appointmentTypes/{id} (Retrieve appointment type)
- [x] PUT /v1/appointmentTypes/{id} (Update appointment type)
- [x] DELETE /v1/appointmentTypes/{id} (Delete appointment type)

## Appointment Outcomes
- [x] GET /v1/appointmentOutcomes (List appointment outcomes)
- [x] POST /v1/appointmentOutcomes (Create appointment outcome)
- [x] GET /v1/appointmentOutcomes/{id} (Retrieve appointment outcome)
- [x] PUT /v1/appointmentOutcomes/{id} (Update appointment outcome)
- [x] DELETE /v1/appointmentOutcomes/{id} (Delete appointment outcome)

## Webhooks
- [x] GET /v1/webhooks (List webhooks)
- [x] POST /v1/webhooks (Create webhook)
- [x] GET /v1/webhooks/{id} (Retrieve webhook)
- [x] PUT /v1/webhooks/{id} (Update webhook)
- [x] DELETE /v1/webhooks/{id} (Delete webhook)

## Webhook Events
- [x] GET /v1/webhookEvents/{id} (Retrieve webhook event)

## Pipelines
- [x] GET /v1/pipelines (List pipelines)
- [x] POST /v1/pipelines (Create pipeline) # Tested: Works.
- [x] GET /v1/pipelines/{id} (Retrieve pipeline)
- [x] PUT /v1/pipelines/{id} (Update pipeline)
- [x] DELETE /v1/pipelines/{id} (Delete pipeline)

## Deals
- [x] GET /v1/deals (List deals)
- [x] POST /v1/deals (Create deal)
- [x] GET /v1/deals/{id} (Retrieve deal)
- [x] PUT /v1/deals/{id} (Update deal) 
- [x] DELETE /v1/deals/{id} (Delete deal)

## Deal Attachments
- [ ] POST /v1/dealAttachments (Add attachment to deal) # TODO: Needs specific API documentation for file upload format
- [ ] GET /v1/dealAttachments/{id} (Retrieve deal attachment) # TODO: Needs specific API documentation
- [ ] PUT /v1/dealAttachments/{id} (Update deal attachment) # TODO: Needs specific API documentation
- [ ] DELETE /v1/dealAttachments/{id} (Delete deal attachment) # TODO: Needs specific API documentation

## Deals Custom Fields
- [x] GET /v1/dealCustomFields (List deal custom fields)
- [x] POST /v1/dealCustomFields (Create deal custom field)
- [x] GET /v1/dealCustomFields/{id} (Retrieve deal custom field)
- [x] PUT /v1/dealCustomFields/{id} (Update deal custom field)
- [x] DELETE /v1/dealCustomFields/{id} (Delete deal custom field)

## Groups
- [x] GET /v1/groups (List groups)
- [x] GET /v1/groups/roundRobin (Get group round robin status)
- [x] POST /v1/groups (Create group)
- [x] GET /v1/groups/{id} (Retrieve group)
- [x] PUT /v1/groups/{id} (Update group)
- [x] DELETE /v1/groups/{id} (Delete group)

## Teams
- [x] GET /v1/teams (List teams)
- [x] POST /v1/teams (Create team)
- [x] GET /v1/teams/{id} (Retrieve team)
- [x] PUT /v1/teams/{id} (Update team)
- [x] DELETE /v1/teams/{id} (Delete team)

## Team Inboxes
- [x] GET /v1/teamInboxes (List team inboxes)

## Ponds
- [x] GET /v1/ponds (List ponds) # Tested: Works
- [ ] POST /v1/ponds (Create pond) # BLOCKED - API rejects field names: "Invalid fields in the request body: user_ids, is_default, description."
- [ ] GET /v1/ponds/{id} (Retrieve pond) # BLOCKED - Prerequisite (POST) fails
- [ ] PUT /v1/ponds/{id} (Update pond) # BLOCKED - Prerequisite (POST) fails
- [ ] DELETE /v1/ponds/{id} (Delete pond) # BLOCKED - Prerequisite (POST) fails

## Inbox Apps
- [x] POST /v1/inboxApps/install (Install inbox app)
- [x] POST /v1/inboxApps/addMessage (Add message to inbox app)
- [x] PUT /v1/inboxApps/updateMessage (Update message in inbox app)
- [x] POST /v1/inboxApps/addNote (Add note to inbox app conversation)
- [x] PUT /v1/inboxApps/updateConversation (Update inbox app conversation)
- [x] GET /v1/inboxApps/getParticipants (Get participants of inbox app conversation)
- [x] POST /v1/inboxApps/addParticipant (Add participant to inbox app conversation) 
- [x] DELETE /v1/inboxApps/removeParticipant (Remove participant from inbox app conversation)
- [x] DELETE /v1/inboxApps/deactivate (Deactivate inbox app)

## Reactions
- [x] POST /v1/reactions/{refType}/{refId} (Create reaction) # Tested: Works (returns [], payload {"body": emoji}).
- [x] GET /v1/reactions/{id} (Retrieve reaction) # Tested: Works. ID discoverable via GET /notes/{id}?includeReactions=true.
- [x] DELETE /v1/reactions/{refType}/{refId} (Delete reaction) # Tested: Works (payload {"body": emoji}, not {"emoji": emoji}).

## Threaded Replies
- [x] GET /v1/threadedReplies/{id} (Retrieve threaded reply) # Tested: Wrapper works (404 for dummy ID as expected).

## Timeframes
- [x] GET /v1/timeframes (List timeframes) 