# Project Assumptions

## Auth
1. User ID, password and names are all in ASCII.
2. All users have different user ID.
3. Users can share the same names and passwords.

## Channels
1. Channels can have identical names, but must have unique channel IDs.

## Channel
1. A message bank is accessible by channel_messages_v1.
2. A user must login before accessing channel details.

## Data Store
1. The order in which users and channels are stored is determined by when they are registered/created.