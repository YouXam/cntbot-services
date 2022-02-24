const config = {
    cos: { // 腾讯云配置
        bucket: "bucket",
        region: 'region',
        secretId: "secretId",
        secretKey: "secretKey"
    },
    mongodb: "mongodb://***" // mongodb 地址
}
const { MongoClient } = require("mongodb")
const COS = require('cos-nodejs-sdk-v5');
const cos = new COS({
    SecretId: config.cos.secretId,
    SecretKey: config.cos.secretKey
});
function list() {
    return new Promise((resolve, reject) => {
        cos.getBucket({
            Bucket: config.cos.bucket,
            Region: config.cos.region
        }, function(err, data) {
            if (err) reject(err)
            else resolve(data)
        });
    })
}
function delete_file(key) {
    return new Promise((res, rej) => {
        cos.deleteObject({
            Bucket: config.cos.bucket,
            Region: config.cos.region,
            Key: key,
        }, function (err, data) {
            if (err) rej(err)
            res(data)
        });
    })
}
async function main(event, context) {
    const client = new MongoClient(config.mongodb)
    await client.connect()
    const db = client.db("cntbot")
    const urls = await db.collection("anime").find().project({ key: 1, key2: 1, blur_key: 1, _id: 0 }).toArray()
    await client.close()
    const tg = new Map()
    urls.forEach(e => {
        tg.set(e.key, true)
        if (e.blur_key) tg.set(e.blur_key, true)
        if (e.key2) tg.set(e.key2, true)
    })
    const filelists = await list()
    const res = []
    filelists.Contents.forEach(async e => {
        const k = '/' + e.Key
        if (tg.get(k)) return
        res.push(k)
        await delete_file(e.Key)
    })
    return {
        code: 0,
        total: res.length,
        res,
    }
};

exports.main_handler = main