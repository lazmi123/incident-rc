# NotebookLM Source: INC-2026-0001 Callback Timeout Restoration

> Demo source only. This is synthetic incident data created to demonstrate the
> NotebookLM workflow. Replace it with approved historical incident data before
> using the assistant for real restoration guidance.

## Source metadata

- Source type: Incident bridge transcript and extracted restoration summary
- Incident ID: INC-2026-0001
- Event name: Bank callback timeout during cash-in transactions
- Service: Callback Service / Middleware Gateway
- Priority: P1
- Major incident: Yes
- Incident start time: 2026-01-14 10:18 BDT
- Detection time: 2026-01-14 10:22 BDT
- Restoration time: 2026-01-14 10:48 BDT
- RCA status: Draft pending approval
- Transcript source: Zoom bridge recording
- Prepared for: NotebookLM incident restoration assistant demo

## Executive summary

Cash-in transactions began failing because the Callback Service was receiving
timeouts from a downstream bank endpoint. The incident bridge identified a spike
in HTTP 504 responses, increased callback queue depth, and stale middleware
connections after a gateway route update. Service was restored by restarting the
callback worker pool, clearing the stuck callback queue, and rolling back the
gateway route change. Middleware, Network, and Bank Integration teams were
involved.

## Mandatory incident fields

| Field | Value |
| --- | --- |
| Incident ID | INC-2026-0001 |
| Event Name | Bank callback timeout during cash-in transactions |
| Service | Callback Service / Middleware Gateway |
| Priority | P1 |
| Major Incident | Yes |
| Impact | Customers could not complete some cash-in transactions; callbacks were delayed or timed out. |
| Root Cause | Gateway route update caused stale middleware connections to the bank callback endpoint. |
| Immediate Mitigation | Restart callback worker pool, clear stuck callback queue, and roll back gateway route change. |
| Permanent Fix | Add gateway route validation and callback timeout monitoring before route changes. |
| Teams Involved | Incident Management, Middleware, Network, Bank Integration, Support |
| RCA Status | Draft pending approval |
| Keywords | callback timeout, HTTP 504, cash-in, middleware, bank endpoint, queue depth |

## Labelled transcript

| Timestamp | Speaker | Role | Transcript |
| --- | --- | --- | --- |
| 00:00:12 | Monjur Morshed | Incident Manager | We have a P1 for cash-in failures. Support reports customers are receiving pending status after submitting transactions. |
| 00:01:05 | Rasel | Middleware Lead | Middleware logs show callback timeout from the bank endpoint. The error is HTTP 504 on the callback service. |
| 00:02:18 | Farhana | Support Lead | Customer complaints started around 10:18. The failure is not universal, but success rate dropped sharply. |
| 00:03:10 | Nayeem | Network Engineer | No packet loss from the application subnet. I can see higher latency on the bank route after the gateway change. |
| 00:04:22 | Rasel | Middleware Lead | Queue depth is increasing. Some callback workers are holding stale connections. I suggest restarting the callback worker pool. |
| 00:05:40 | Monjur Morshed | Incident Manager | Rasel, please restart callback workers and confirm whether queue depth reduces. Nayeem, check the gateway route change and prepare rollback if needed. |
| 00:08:15 | Rasel | Middleware Lead | Callback worker restart completed. New callbacks are moving, but older items are still stuck in the queue. |
| 00:10:04 | Farhana | Support Lead | Support confirms new customer attempts are improving, but previous transactions remain pending. |
| 00:11:30 | Nayeem | Network Engineer | The route change was applied at 10:16. I recommend rollback because latency increased immediately afterward. |
| 00:12:20 | Monjur Morshed | Incident Manager | Decision: roll back the gateway route change. Middleware will clear stuck queue items after rollback. |
| 00:15:45 | Nayeem | Network Engineer | Gateway rollback completed. Latency to bank endpoint is back to normal range. |
| 00:17:05 | Rasel | Middleware Lead | I am clearing stuck callback queue items in batches to avoid duplicate callbacks. |
| 00:20:35 | Rasel | Middleware Lead | Queue depth is down by 80 percent. Callback success rate is above 97 percent. |
| 00:23:50 | Farhana | Support Lead | Customer complaints have slowed. We need a list of affected transaction IDs for proactive communication. |
| 00:25:10 | Monjur Morshed | Incident Manager | Restoration criteria: callback success rate stable above 98 percent for 10 minutes and pending queue below normal threshold. |
| 00:31:05 | Rasel | Middleware Lead | Queue is back to normal threshold. No new HTTP 504 errors in the last 8 minutes. |
| 00:34:30 | Farhana | Support Lead | Support confirms cash-in success is normal again. Pending customers are being updated. |
| 00:36:00 | Monjur Morshed | Incident Manager | We are marking service restored at 10:48. RCA needs gateway validation and callback monitoring actions. |

## Restoration timeline

| Time | Event | Evidence |
| --- | --- | --- |
| 10:18 BDT | Customer impact begins. | Support reported complaints started around 10:18 at transcript 00:02:18. |
| 10:22 BDT | Incident detected and P1 bridge started. | Incident Manager opened the bridge at transcript 00:00:12. |
| 10:27 BDT | Callback timeout and HTTP 504 pattern identified. | Middleware Lead reported HTTP 504 from bank endpoint at transcript 00:01:05. |
| 10:31 BDT | Callback worker restart assigned. | Incident Manager assigned restart at transcript 00:05:40. |
| 10:34 BDT | Callback worker restart completed. | Middleware Lead confirmed restart at transcript 00:08:15. |
| 10:38 BDT | Gateway route rollback approved. | Incident Manager recorded decision at transcript 00:12:20. |
| 10:41 BDT | Gateway rollback completed. | Network Engineer confirmed rollback at transcript 00:15:45. |
| 10:43 BDT | Stuck callback queue clearing started. | Middleware Lead reported queue clearing at transcript 00:17:05. |
| 10:48 BDT | Service restored. | Incident Manager marked restoration at transcript 00:36:00. |

## Action items

| Time | Owner | Action | Status | Evidence |
| --- | --- | --- | --- | --- |
| 00:05:40 | Middleware Team | Restart callback worker pool. | Completed | Assigned by Incident Manager and confirmed at 00:08:15. |
| 00:05:40 | Network Team | Check gateway route change and prepare rollback. | Completed | Assigned by Incident Manager and confirmed at 00:11:30. |
| 00:12:20 | Network Team | Roll back gateway route change. | Completed | Decision recorded at 00:12:20 and completed at 00:15:45. |
| 00:17:05 | Middleware Team | Clear stuck callback queue items in batches. | Completed | Progress reported at 00:20:35 and normal threshold reached at 00:31:05. |
| 00:23:50 | Support Team | Prepare affected transaction ID list for customer communication. | In Progress | Requested by Support Lead at 00:23:50. |
| 00:36:00 | Middleware and Network Teams | Add gateway validation and callback timeout monitoring to RCA. | Open | Requested by Incident Manager at 00:36:00. |

## Decisions

| Time | Decision | Decision owner | Evidence |
| --- | --- | --- | --- |
| 00:12:20 | Roll back the gateway route change. | Incident Manager | Network reported latency increase after the route change at 00:11:30. |
| 00:25:10 | Restoration criteria require callback success rate above 98 percent for 10 minutes and pending queue below normal threshold. | Incident Manager | Criteria stated directly at 00:25:10. |
| 00:36:00 | Mark service restored at 10:48 BDT. | Incident Manager | Support and Middleware confirmed normal status at 00:31:05 and 00:34:30. |

## Escalations

| Time | Team | Reason | Status |
| --- | --- | --- | --- |
| 00:03:10 | Network Team | Validate latency and route behavior to bank endpoint. | Completed |
| 00:04:22 | Middleware Team | Investigate queue depth and stale callback worker connections. | Completed |
| 00:23:50 | Support Team | Identify affected customers and transaction IDs. | In Progress |

## Similar incident recommendation signals

Use this incident as a similar reference when a new incident includes one or
more of these signals:

- HTTP 504 timeout from a bank or partner callback endpoint.
- Callback queue depth increasing during cash-in or payment flows.
- Stale middleware connections after route, gateway, or network changes.
- Customers seeing pending transaction status after submission.
- Service restored through worker restart, queue clearing, or route rollback.

## Recommended investigation steps for similar incidents

These recommendations are valid only when a similar incident is retrieved and
cited:

1. Check callback service logs for HTTP 504 or timeout errors.
2. Compare incident start time with recent gateway, route, firewall, or partner
   connectivity changes.
3. Inspect callback queue depth and worker connection age.
4. Restart callback workers only if stale connections are confirmed.
5. Validate whether route rollback is needed when latency increased after a
   network change.
6. Clear stuck queue items in controlled batches to avoid duplicate callbacks.
7. Confirm restoration using success-rate and pending-queue thresholds.

## Lessons learned

- Gateway route changes need pre-change and post-change callback latency checks.
- Callback queues need alerts before backlog becomes customer visible.
- The incident bridge should record restoration criteria early.
- Customer-impact reports from Support helped validate recovery.

## Mandatory source citation block

- Similar incident used: INC-2026-0001
- Transcript references: 00:01:05, 00:04:22, 00:05:40, 00:12:20, 00:15:45,
  00:17:05, 00:31:05, 00:36:00
- RCA reference: Draft RCA pending approval
- Confidence score: 0.88
- Confidence reason: Transcript contains clear evidence for timeout symptom,
  route rollback, worker restart, and restoration time. Permanent fix remains
  pending RCA approval.

## Grounding instruction for NotebookLM

When answering from this source, cite the incident ID and transcript timestamps.
If no matching evidence appears in this source or other uploaded approved
incident sources, state that no relevant incident history was identified.
