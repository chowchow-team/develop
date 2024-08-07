import React from "react";
import { Helmet } from "react-helmet-async";

function SEOMetaTag({ title, description, keywords, image, url}) {
    // 인덱스에 픽스된 메타태그만 남기고, 중복되는거 제거해야됨.
    return (
        <Helmet>
            <title>{title}</title>
            <meta name="description" content={description} />
            <meta name="keywords" content={keywords} />

            <meta property="og:title" content={title} />
            <meta property="og:description" content={description} />
            <meta property="og:image" content={image} />
            <meta property="og:url" content={url} />
            <meta property="og:type" content='website' />

            <link rel="canonical" href={url}></link>
            <meta name="robots" content="index,follow"/>
        </Helmet>
    );
}

export default SEOMetaTag;