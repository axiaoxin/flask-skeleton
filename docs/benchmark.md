title: 简单总结的压测数据
date: 2018-06-28
tag: []

    send_email_time: 0.05s
    cpucount: 8

    ---------------------------

    apiserver: 1 sync worker 任务入队 500+-/s
    apiserver: cpucount 8 sync worker 任务入队 1300+-/s
    apiserver: cpucount*2+1 17 sync worker 任务入队 1300+-/s

    apiserver: 1 gevent worker 任务入队 600+-/s
    apiserver: cpucount 8 gevent worker 任务入队 2200+-/s
    apiserver: cpucount*2+1 17 gevent worker 任务入队 2400+-/s

    ----------------------------

    apiserver: 1 sync worker 220+-r/s 400ms
    apiserver: cpucount 8 sync worker  840+-r/s 180ms
    apiserver: cpucount*2+1 17 sync worker  800+-r/s 200ms

    apiserver: 1 gevent worker  220+-r/s 350ms
    apiserver: cpucount 8 gevent worker 790r/s 350ms
    apiserver: cpucount*2+1 17 gevent worker 790r/s 450ms

    # 因为消息入口接口返回非常快，所以gevent worker的优势不明显

    -----------------------------

    apiserver master: 138.8m VIRT 18.8m RES 4.8m SHR
    apiserver worker: 204.4m VIRT 40.5m RES 3.2m SHR


    celery prefork master worker: 201m VIRT 47.8m RES 5.1m SHR
    celery prefork worker: 199.4m VIRT 40.9m RES 2m SHR

    1 master worker prefork concurrency=8 consumer ack: 148/s cpu 30%
    2 master worker prefork concurrency=8 consumer ack: 290/s cpu 25% *
    1 master worker prefork concurrency=16 consumer ack: 260/s cpu 40%
    2 master worker prefork concurrency=16 consumer ack: 470/s cpu 35%
    1 master worker prefork concurrency=32 consumer ack: 280/s cpu 40%

    celery gevent worker: 354m VIRT 48.6m RES 5.7m SHR

    1 worker gevent concurrency=8 consumer ack: 132/s cpu 40%
    1 worker gevent concurrency=16 consumer ack: 170/s cpu 50%
    1 worker gevent concurrency=32 consumer ack: 225/s cpu 67% *
    1 worker gevent concurrency=64 consumer ack: 235/s cpu 70%
    2 worker gevent concurrency=8 consumer ack: 260/s cpu 40%
    2 worker gevent concurrency=16 consumer ack: 355/s cpu 50%
    2 worker gevent concurrency=32 consumer ack: 420/s cpu 60%
    2 worker gevent concurrency=64 consumer ack: 430/s cpu 70%
