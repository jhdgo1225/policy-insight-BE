#!/bin/bash
pg_dump -U postgres policyinsight > /backup/policyinsight_$(date +%Y%m%d_%H%M%S).sql